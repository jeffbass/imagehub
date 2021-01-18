"""imagehub: receive and save images and events from imagenodes

Receives and stores event messages and event images from multiple
sources simultaneously. The sources are Raspberry Pi (and other) computers
running imaganode.py to capture and send selected images and event messages.

Typically run as a service or background process. See README.rst for details.

Copyright (c) 2020 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import sys
import signal
import logging
import logging.handlers
import traceback
import argparse
from tools.utils import clean_shutdown_when_killed
from tools.hub import Settings
from tools.hub import ImageHub

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False,
	help="path to imagehub.yaml file")
args = vars(ap.parse_args())

def main():
    # set up controlled shutdown when Kill Process or SIGTERM received
    signal.signal(signal.SIGTERM, clean_shutdown_when_killed)
    settings = Settings(path=args["path"])  # get settings from YAML file
    hub = ImageHub(settings)  # start ImageWriter, Timers, etc.
    log = start_logging(hub)
    log.info('Starting imagehub.py')
    try:
        # forever event loop: receive & process images and text from imagenodes
        while True:
            text, image = hub.receive_next()
            reply = hub.process(text, image, settings)
            hub.send_reply(reply)
    except (KeyboardInterrupt, SystemExit):
        log.warning('Ctrl-C was pressed or SIGTERM was received.')
    except Exception as ex:  # traceback will appear in log
        log.exception('Unanticipated error with no Exception handler.')
    finally:
        if 'hub' in locals():
            hub.closeall()
        log.info('Exiting imagehub.py')
        sys.exit()

def start_logging(hub):
    log = logging.getLogger()
    handler = logging.handlers.TimedRotatingFileHandler(hub.logfile,
        when='midnight', backupCount=995)
    formatter = logging.Formatter('%(asctime)s ~ %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    hub.log = log
    return log

if __name__ == '__main__' :
    main()
