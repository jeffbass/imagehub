#!/bin/bash

# imagehub.sh: a way to start imagehub.py at startup
#   needs to be adapted to use with cron, screen, or systemctl service
#   e.g., workon expects you are executing this script from home directory
source $(which virtualenvwrapper.sh)
workon py3cv3  # replace with your virtualenv name
cd /home/pi/imagehub/imagehub  # on RPi; change for Mac or Linux
nohup python imagehub.py </dev/null >imagehub.stdout 2>imagehub.stderr &
