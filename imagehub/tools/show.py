"""hub.py -- ImagHub and Settings classes

Copyright (c) 2018 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import os
import sys
import yaml
import pprint
import signal
import itertools
from time import sleep
from ast import literal_eval
from datetime import datetime
from collections import deque
import numpy as np
import cv2
import imutils
from tools.utils import interval_timer
from tools.hubhealth import HealthMonitor

class Hubshow:
    """ Contains the attributes and methods of an imagehub

    One ImageHub is instantiated during the startup of the imagehub.py
    """
    def __init__(self, settings):
        # Check that numpy and OpenCV are OK; will get traceback error if not
        self.tiny_image = np.zeros((3,3), dtype="uint8")  # tiny blank image
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", self.tiny_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        self.tiny_jpg = jpg_buffer # matching tiny blank jpeg

        self.userdir = settings.userdir  # the users home directory ~

        # check that data and log directories exist
        # see docs for data directory structure including logs and images
        self.data_directory = os.path.join(self.userdir, settings.data_directory)
        self.log_directory = os.path.join(self.data_directory, 'logs')
        self.logfile = os.path.join(self.log_directory, 'imagehub.log')
        self.images_directory = os.path.join(self.data_directory, 'images')

    def menu():
        pass

    def read_command():
        pass

    def display_results():
        pass
