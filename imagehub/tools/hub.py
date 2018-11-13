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
from collections import deque
import numpy as np
import cv2
import imutils
from imutils.video import VideoStream
sys.path.insert(0, '../../imagezmq/imagezmq') # for testing
import imagezmq
from tools.utils import interval_timer
from tools.nodehealth import HealthMonitor

class ImageHub:
    """ Contains all the attributes and methods of this imagehub

    One ImageHub is instantiated during the startup of the imagehub.py
    program. It takes the settings loaded from the YAML file and sets all
    the operational parameters of the imagehub, including the hub address and
    port to receive messages, directories to store images and logs, etc.

    The ImageHub also has methods to write files from inbound message queue
    to directories.

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
        self.health = HealthMonitor(settings, self.image_q)

        # open ZMQ hub using imagezmq
        self.image_hub = imagezmq.ImageHub()

    def process(self, text, image):
        ''' process one incoming message

        Every node message has a text part and an image part

        There are 2 formats for the node message text part:
        Event message: nodename viewname | event_type | optional added info
        Image message: nodename viewname | image_type ('jpg' or 'image')

        See docs/imagehub-details.rst for more about message formats

        '''
        message = text.split("|")
        node_and_view = message[0]  # not using this in current version
        type = message[1]  # type is the second delimited field in text
        t0 = type[0]  # the first character of type is unique & compares faster

        if t0 == 'H':  # Heartbeat message; fast return before testing anyting else
            return 'OK'
        elif t0 == "i":  # image
            self.image_q.append((node_and_view, image, t0,))
        elif t0 == 'j':  # jpg
            self.image_q.append((node_and_view, image, t0,))
        else:
            hub.log.info(text)
        return 'OK'

    def fix_comm_link(self):
        """ Evaluate, repair and restart communications link with hub.

        Restart link if possible, else restart program or reboot computer.
        """

        print('Fixing broken comm link...')
        print('....by ending the program.')
        raise KeyboardInterrupt
        return 'hub_reply'
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
            self.patience = 10  # default is to wait 10 seconds for hub reply
        if 'queuemax' in self.config['hub']:
            self.queuemax = self.config['hub']['queuemax']
        else:
            self.queuemax = 500
        if 'image_directory' in self.config['hub']:
            self.image_directory = self.config['hub']['image_directory']
        else:
            self.image_directory = 'imagehub_data'
        if 'log_directory' in self.config['hub']:
            self.log_directory = self.config['hub']['log_directory']
        else:
            self.log_directory = 'imagehub_logs'

    def print_settings(self, title=None):
        """ prints the settings in the yaml file using pprint()
        """
        if title:
            print(title)
        print('Contents of imagehub.yaml:')
        pprint.pprint(self.config)
        print()
