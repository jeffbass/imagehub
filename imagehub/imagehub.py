"""imagehub: receive and save images and events from imagenodes

Receives and stores event messages and event images from multiple
sources simultaneously. The sources are Raspberry Pi (and other) computers
running imaganode.py to capture and send selected images and event messages.

Typically run as a service or background process. See README.rst for details.

Copyright (c) 2018 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import sys
import signal
import logging
import logging.handlers
import traceback
from tools.utils import clean_shutdown_when_killed
from tools.utils import Patience
from tools.hub import Settings
from tools.hub import ImageHub

def main():
    # set up controlled shutdown when Kill Process or SIGTERM received
    signal.signal(signal.SIGTERM, clean_shutdown_when_killed)
    settings = Settings()  # get settings from YAML file
    hub = ImageHub(settings)  # start ImageWriter, Timers, etc.
    log = start_logging(hub)
    log.info('Starting imagehub.py')
    try:
        # forever event loop
        while True:
            try:
                with Patience(hub.patience):
                    text, image = hub.receive_next()
            except Patience.Timeout:  # if no timely message from any node
                hub.handle_timeout()
                continue
            reply = hub.process(text, image)
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
    handler = logging.handlers.RotatingFileHandler(hub.logfile,
        maxBytes=15000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s ~ %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    hub.log = log
    return log

if __name__ == '__main__' :
    main()
