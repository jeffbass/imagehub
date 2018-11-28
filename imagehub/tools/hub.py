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
        test_image = cv2.imdecode(np.fromstring(jpg_buffer, dtype='uint8'), -1)
        print('Tiny image translated to jpg and back OK:',
            np.array_equal(self.tiny_image, test_image))

        # image queue of (node_and_view, image, type) to write to image directory
        self.image_q = deque(maxlen=settings.queuemax)
        # start system health monitoring & get system type (RPi vs Mac etc)
        self.health = HealthMonitor(settings)

        self.patience = settings.patience * 60  # convert to seconds

        # open ZMQ hub using imagezmq
        self.image_hub = imagezmq.ImageHub()
        self.receive_next = self.image_hub.recv_jpg  # assume receving jpg
        self.send_reply = self.image_hub.send_reply

        # check that data and log directories exist; create them if not
        self.data_directory = self.build_dir(settings.data_directory, settings)
        log_directory = os.path.join(self.data_directory, 'logs')
        self.log_directory = self.build_dir(log_directory, settings)
        self.logfile = os.path.join(self.log_directory, 'imagehub.log')
        images_directory = os.path.join(self.data_directory, 'images')
        self.images_directory = self.build_dir(images_directory, settings)
        print('data directory:', self.data_directory)
        print('log directory:', self.log_directory)
        print('log file:', self.logfile)
        print('images directory:', self.images_directory)
        self.log = None

    def build_dir(self, directory, settings):
        """Build full directory name from settings directory from yaml file
        """
        full_directory = os.path.join(settings.userdir,directory)
        try:
            os.mkdir(full_directory)
        except FileExistsError:
            pass
        return full_directory


    def process(self, text, image):
        ''' process one incoming node message

        Every node message has a text part and an image part

        There are 2 formats for the node message text part:
        Event message: nodename viewname | event_type | optional added info
        Image message: nodename viewname | image_type
            (where image_type is either 'jpg' or 'image')

        See docs/imagehub-details.rst for more about message formats

        '''
        message = text.split("|")
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
            # writing image files from image_q will be done in thread later
            # for testing for now, pop image_q and write the image file here
            self.write_one_image()
        else:
            log_text = timestamp + ' ~ ' + text
            self.log.info(log_text)
            print(log_text)
        return b'OK'

    def write_one_image(self):
        filename, image, type = self.image_q.popleft()
        print('filename and image type:', filename, type)
        pass

    def handle_timeout(self):
        timestamp = datetime.now().isoformat().replace(':', '.')
        message = timestamp + ' ~ ' + 'No messages received for ' + str(
            self.patience // 60) + ' minutes.'
        self.log.info(message)
        pass

    def closeall(self):
        """ Close all resources & write any images remaining in image_q.
        """
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

    def __init__(self):
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

    def print_settings(self, title=None):
        """ prints the settings in the yaml file using pprint()
        """
        if title:
            print(title)
        print('Contents of imagehub.yaml:')
        pprint.pprint(self.config)
        print()
