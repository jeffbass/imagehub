"""hubshow: show images and events from imagehub

Lists event messages and shows images received and saved by imagehub.py. Uses
the same imagehub.yaml file to get settings to find log and image files.

This is an interactive "helper program" to provide simple listings of event logs
and viewing of selected images that have been collected by imagehub.py.

Run the program in the same virtual environment used by imagehub.py. See
documentation for details.

Copyright (c) 2018 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import sys
import signal
import traceback
from tools.utils import clean_shutdown_when_killed
from tools.utils import Patience
from tools.hub import Settings
from tools.show import Hubshow

def main():
    # set up controlled shutdown when Kill Process or SIGTERM received
    signal.signal(signal.SIGTERM, clean_shutdown_when_killed)
    settings = Settings()  # get settings from YAML file
    show = HubShow(settings)
    try:
        show.menu()
        while True:
            show.read_command()
            show.display_results()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as ex:
        print('Unanticipated error with no Exception handler.')
        print(traceback.format_exc())
    finally:
        sys.exit()

if __name__ == '__main__' :
    main()
