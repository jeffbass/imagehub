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
        pass

    def menu():
        pass

    def read_command():
        pass

    def display_results():
        pass
