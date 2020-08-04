"""hub.py -- ImagHub and Settings classes

Copyright (c) 2018 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import os
import sys
import yaml
import pprint
import signal
import logging
import itertools
import threading
from time import sleep
from ast import literal_eval
from datetime import datetime
from collections import deque
import numpy as np
import cv2
import imutils
from imutils.video import VideoStream
sys.path.insert(0, '../../imagezmq/imagezmq') # for testing
import imagezmq
from tools.utils import interval_timer
from tools.hubhealth import HealthMonitor

class ImageHub:
    """ Contains the attributes and methods of an imagehub

    One ImageHub is instantiated during the startup of the imagehub.py
    program. It takes the settings loaded from the YAML file and sets all
    the operational parameters of the imagehub, including the hub address and
    port to receive messages, directories to store images and logs, etc.

    The ImageHub has methods to write events from inbound message queue
    to the event log and to write inbound image files to image directories.

    Parameters:
        settings (Settings object): settings object created from YAML file
    """

    def __init__(self, settings):
        # Check that numpy and OpenCV are OK; will get traceback error if not
        self.tiny_image = np.zeros((3,3), dtype="uint8")  # tiny blank image
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", self.tiny_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        self.tiny_jpg = jpg_buffer # matching tiny blank jpeg

        # image queue of (node_and_view, image, type) to write to image directory
        self.image_q = deque(maxlen=settings.queuemax)
        # start system health monitoring & get system type (RPi vs Mac etc)
        self.health = HealthMonitor(settings)

        self.patience = settings.patience * 60  # convert to seconds
        self.userdir = settings.userdir

        # open ZMQ hub using imagezmq
        self.image_hub = imagezmq.ImageHub()
        self.receive_next = self.image_hub.recv_jpg  # assume receving jpg
        self.send_reply = self.image_hub.send_reply

        # check that data and log directories exist; create them if not
        # see docs for data directory structure including logs and images
        self.data_directory = self.build_dir(settings.data_directory)
        log_directory = os.path.join(self.data_directory, 'logs')
        self.log_directory = self.build_dir(log_directory)
        self.logfile = os.path.join(self.log_directory, 'imagehub.log')
        images_directory = os.path.join(self.data_directory, 'images')
        self.images_directory = self.build_dir(images_directory)
        self.log = None

        self.max_images_write = settings.max_images_write
        self.image_count = 0  # count of images written in current directory
        self.first_time_over_max = True  # is this the first time max exceeded?
        self.image_writing_thread = threading.Thread(daemon=True,
                                    target=self.image_writer)
        self.keep_writing = True
        self.image_writing_thread.start()

    def build_dir(self, directory):
        """Build full directory name from settings directory from yaml file
        """
        full_directory = os.path.join(self.userdir, directory)
        try:
            os.mkdir(full_directory)
            self.image_count = 0  # Each new image directory gets a new 0 count
            self.first_time_over = True  # if exceeded, this is first time
        except FileExistsError:
            pass
        return full_directory


    def process(self, text, image, settings):
        ''' process one incoming node message

        Every node message has a text part and an image part

        There are 2 formats for the node message text part:
        Event message: nodename viewname | event_type | optional added info
        Image message: nodename viewname | image_type
            (where image_type is either 'jpg' or 'image')

        See docs/imagehub-details.rst for more about message formats

        '''
        message = text.split("|")
        if len(message) < 2:  # a "send_test_image" that should not be saved
            return b'OK'
        type = message[1]  # type is the second delimited field in text
        t0 = type[0]  # the first character of type is unique & compares faster
        if t0 == 'H':  # Heartbeat message; return before testing anything else
            return b'OK'
        node_and_view = message[0].strip().replace(' ', '-')
        # datetime.now().isoformat() looks like '2013-11-18T08:18:31.809000'
        timestamp = datetime.now().isoformat().replace(':', '.')
        image_filename = node_and_view + '-' + timestamp

        if t0 == "i":  # image
            pass  # ignore image type; only saving jpg images for now
        elif t0 == 'j':  # jpg; append to image_q
            self.image_q.append((image_filename, image, t0,))
            # writing image files from image_q is normally done in a thread
            # but for unthreaded testing, uncomment below to write every image
            # self.write_one_image()
        else:
            log_text = text  # may strip spaces later?
            self.log.info(log_text)
        return b'OK'

    def image_writer(self):
        # writes all the images in the image_q
        # run as a separate thread, started in the class constructor
        while self.keep_writing:
            if len(self.image_q) > 0:
                self.write_one_image()
            else:
                sleep(0.0000001) # sleep before checking image_q again

    def write_one_image(self):
        # when actually writing images, need to stop if too many have been
        # written, to prevent disk fillup; need to set limits in imagehub.yaml
        filename, image, type = self.image_q.popleft()
        date = filename[-26:-16]
        date_directory = os.path.join(self.images_directory, date)
        date_directory = self.build_dir(date_directory)
        self.image_count += 1
        if self.image_count > self.max_images_write:
            if self.first_time_over_max:
                self.log.warning('Max images written. Writing stopped.')
                self.first_time_over_max = False
            return  # This directory has hit its maximum number of images
        full_file_name = os.path.join(date_directory, filename) + ".jpg"
        # write the image file to disk using full_file_name
        with open(full_file_name,"wb") as f:
            f.write(image)

    def handle_timeout(self):
        timestamp = datetime.now().isoformat().replace(':', '.')
        message = 'No messages received for ' + str(
            self.patience // 60) + ' minutes.'
        self.log.info(message)
        pass

    def closeall(self):
        """ Close all resources & write any images remaining in image_q.
        """
        # write any any images left in queue to files
        self.keep_writing = False  # signals the image writing thread to stop
        # wait for 1 second, then write any images left in the image_q
        sleep(1)
        while len(self.image_q) > 0:
            self.write_one_image()
        pass

class Settings:
    """Load settings from YAML file

    Note that there is currently almost NO error checking for the YAML
    settings file. Therefore, by design, an exception will be raised
    when a required setting is missing or misspelled in the YAML file.
    This stops the program with a Traceback which will indicate which
    setting below caused the error. Reading the Traceback will indicate
    which line below caused the error. Fix the YAML file and rerun the
    program until the YAML settings file is read correctly.

    There is a "print_settings" option that can be set to TRUE to print
    the dictionary that results from reading the YAML file. Note that the
    order of the items in the dictionary will not necessarily be the order
    of the items in the YAML file (this is a property of Python dictionaries).
    """

    def __init__(self, path):
        if path:
            userdir = path
        else:
            userdir = os.path.expanduser("~")
        self.userdir = userdir
        with open(os.path.join(userdir,"imagehub.yaml")) as f:
            self.config = yaml.safe_load(f)
        self.print_hub = False
        if 'hub' in self.config:
            if 'print_settings' in self.config['hub']:
                if self.config['hub']['print_settings']:
                    self.print_settings()
                    self.print_hub = True
                else:
                    self.print_hub = False
        else:
            self.print_settings('"hub" is a required settings section but not present.')
            raise KeyboardInterrupt
        if 'patience' in self.config['hub']:
            self.patience = self.config['hub']['patience']
        else:
            self.patience = 10  # default is to wait 10 minutes for imagenodes
        if 'queuemax' in self.config['hub']:
            self.queuemax = self.config['hub']['queuemax']
        else:
            self.queuemax = 500
        if 'data_directory' in self.config['hub']:
            self.data_directory = self.config['hub']['data_directory']
        else:
            self.data_directory = 'imagehub_data'
        if 'max_images_write' in self.config['hub']:
            self.max_images_write = self.config['hub']['max_images_write']
        else:
            self.max_images_write = 5000

    def print_settings(self, title=None):
        """ prints the settings in the yaml file using pprint()
        """
        if title:
            print(title)
        print('Contents of imagehub.yaml:')
        pprint.pprint(self.config)
        print()
