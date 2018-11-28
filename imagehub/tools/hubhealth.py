"""hubhealth: network and system stability classes

Copyright (c) 2017 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import logging
import platform
import threading
import numpy as np
from tools.utils import interval_timer

class HealthMonitor:
    """ Methods and attributes to measure and tune network and system stability

    Provides methods to send network heartbeat messages, determine system type
    (e.g., Raspberry Pi vs. Mac), and fix problems.

    Mostly a few example methods so far; send_heartbeat() has been very helpful
    in fixing some odd WiFi networking problems.

    Parameters:
        settings (Settings object): settings object created from YAML file
    """
    def __init__(self, settings):
        self.sys_type = self.get_sys_type()

    def get_sys_type(self):
        """ determine system type, e.g., RPi or Mac
        """
        uname = platform.uname()
        if uname.system == 'Darwin':
            return 'Mac'
        elif uname.system == 'Linux':
            with open('/etc/os-release') as f:
                osrelease = f.read()
                if 'raspbian' in osrelease.lower():
                    return 'RPi'
                elif 'ubuntu' in osrelease.lower():
                    return 'Ubuntu'
                else:
                    return 'Linux'
        else:
            return 'Unknown'

    def reboot_this_computer(self):
        if self.sys_type == 'RPi':  # reboot only if RPi
            print('This is a mock reboot.')

    def check_ping(self, address='192.168.1.1'):
        return 'OK'  # for testing

def main():
    settings = None
    health = HealthMonitor(settings)
    print('This computer is ', health.sys_type)
    ping_OK = health.check_ping()
    print('Ping Check is ', ping_OK)
    health.reboot_this_computer()

if __name__ == '__main__' :
    main()
