============================================================
imagehub: Receive & save images from multiple Raspberry Pi's
============================================================

Introduction
============

**imagehub** receives and stores images and event messages from multiple
sources simultaneously. The sources are Raspberry Pi and other computers
running **imaganode** to capture and send images and event messages.

Here is a pair of images shown with their corresponding log entries. These were
captured by a Raspberry Pi PiCamera and an infrared floodlight:

.. image:: docs/images/coyote-events.png

The log shows the coyote motion events (in **bold**) as "Barn". It also shows
events from 2 other Raspberry Pi computers that were sending at the same time,
"WaterMeter" and "BackDeck". Motion events create camera images like the
2 shown above. Temperature events are gathered by sensors attached to the
Raspberry Pi computers' GPIO pins.

.. contents::

Overview
========

**imagehub** is the "receive and store" part of a distributed computer vision
pipeline that is run on multiple computers. Multiple Raspberry Pi
(and other) computers run **imagenode** to capture images, detect motion, light,
temperature values, etc. **Imagenode** then sends event messages and selected
images to **imagehub**, which files the events and images for later
analysis.  My typical setup has 8 to 12 sending computers for each **imagehub**.

By design, **imagehub** is a very simple program. It does 2 things:

1. It receives images and stores them.
2. It receives event messages and logs them.

It does this from multiple sources simultaneously. The sources are typically a
bunch of Raspberry Pi computers with PiCameras and temperature sensors. Keeping
**imagehub** simple allows it to be fast enough to reliably store data from
multiple sources. Analysis of images and responses to queries
are handled by other programs. See `Using imagenode in distributed computer
vision projects <https://github.com/jeffbass/imagenode/imagenode-uses.rst>_`
for a more detailed explanation of the overall project design. See the
`Yin Yang Ranch project <https://github.com/jeffbass/yin-yang-ranch>`_
for more details about the architecture of the
**imagenode** <--> **imagezmq** <--> **imagehub** system.



imagehub Features
=================

- Receives and save images from multiple Raspberry Pi's simultaneously.
- Receives and logs event messages from multiple RPi's simultaneously.
- Uses threading for image writing to enhance responsiveness.
- Threading can be replaced with multiprocessing with minimal code changes.

Dependencies and Installation
=============================

**imagehub** has been tested with:

- Python 3.5 and 3.6
- OpenCV 3.3
- PyZMQ 16.0
- imagezmq 0.0.2

**imagehub** uses **imagezmq** to receive event messages and images that are
captured and sent by **imagenode**. You will need to install and test both
**imagezmq** and **imagenode** before using **imagehub**.
The instructions for installing and testing **imagezmq** are in the
`imagezmq GitHub repository <https://github.com/jeffbass/imagezmq.git>`_.
The instructions for installing and testing **imagenode** are in the
`imagenode GitHub repository <https://github.com/jeffbass/imagenode.git>`_.

**imagehub** is still in early development, so it is not yet in PyPI. Get it by
cloning the GitHub repository::

    git clone https://github.com/jeffbass/imagehub.git

Once you have cloned **imagehub** to a directory on your local machine,
you can run the tests using the instructions below. The instructions assume you
have cloned both **imagehub** and **imagezmq** to the user home directory. It
is also important that you have successfully run all the tests for **imagezmq**
and for **imagenode**. The recommended testing arrangement is to run **imagehub**
on the same Mac (or other display computer) that you used to run the
``imagezmq/tests/timing_receive_jpg_buf.py`` program when you tested **imagenode**.

Running the Tests
=================

**imagehub** should be tested after you have tested **imagenode**, because you
will be using **imagenode** to send test images and event messages to
**imagehub**.

Test **imagehub** in the same virtualenv that you tested **imagenzmq** in. For
the **imagezmq** testing and for the **imagenode** testing, my virtualenv is
called py3cv3.

To test **imagehub**, you will use the same setup as Test 2 for **imagenode**
(see  `The imagezmq classes that allow transfer of images <https://github.com/jeffbass/imagezmq>`_).
You will run **imagenode** on a Raspberry Pi with a PiCamera, just as you did for
**imagenode** Test 2. You will run **imagehub** on the same Mac (or other display
computer) that you used to display the **imagenode** test images.

Directory Structure for running the imagehub tests
--------------------------------------------------
Neither **imagehub** or **imagezmq** are far enough along in their development
to be pip installable. So they should both be git-cloned to the computer that
they will be running on. I have done all testing at the user home
directory. Here is a simplified directory layout::

  ~ # user home directory of the computer running imagehub
  +--- imagehub.yaml  # copied from imagenode/imagenode.yaml
  |
  +--- imagehub    # the git-cloned directory for imagehub
  |    +--- sub directories include docs, imagehub, tests
  |
  +--- imagezmq    # the git-cloned directory for imagezmq
  |   +--- sub directories include docs, imagezmq, tests
  |
  +--- imagehub_data   # this directory will be created by imagehub
      +--- images      # images will be saved here
      +--- logs        # logs containing event messages will be saved here

This directory arrangement, including docs, imagenode code, tests, etc. is a
common development directory arrangement on GitHub. Using git clone from your
user home directory (either on a Mac, a RPi or other Linux computer) will
put both the **imagenode** and **imagezmq** directories in the right place
for testing. The **imagehub** program creates a directory (imagehub_data) and
2 subdirectories (images and logs) to store the images and logs of event
messages it receives from **imagenode** running on one or more RPi's or other
computers.

Test 1: Running **imagehub** with a single **imagenode** sender
---------------------------------------------------------------
**The first test** uses a single Raspberry Pi computer running **imagenode**
with **imagehub** running on Mac or other display computer.
It tests that the **imagehub** software is installed correctly and that the
``imagehub.yaml`` file has been copied and edited in a way that works.

Test 2: Running **imagehub** with 2 **imagenode** senders simultaneously
------------------------------------------------------------------------
**The second test** runs **imagenode** on 2 Raspberry Pi computers,
with **imagehub** receiving images and event messages from both RPi's at
the same time. The event logs and image files will record what is sent
from both RPi's.

Further details of running the tests are `here <docs/testing.rst>`_.

Running **imagehub** in production
==================================
Running the test programs requires that you leave a terminal window open, which
is helpful for testing, but not for production runs. I have provided an example
imagehub.sh shell script that shows how I start **imagehub** for the production
programs observing my small farm. The key is to start the imagehub.py program
1) in the correct virtualenv and 2) as a background task that allows the program
to keep running when the terminal window is closed. There are multiple ways to
start the imagehub.sh program when the RPi starts: use cron, use screen, or use
the systemctl / systemd service protocol that linux services use for startup.
The best one to use is the one that you prefer and are familiar with, so I won't
make a specific recommendation here.

In production, you would want to set the test options used to print settings
to false; they are only helpful during testing. All errors and information
are sent to imagehub.log in the same directory as imagehub.py. You will
probably want the log to be in a different directory for production; the log
file location can be set by changing it in the logging function at the bottom
of the imagehub.py program file.

Additional Documentation
========================
- `How imagehub works <docs/imagehub-details.rst>`_.
- `The imagezmq classes that allow transfer of images <https://github.com/jeffbass/imagezmq>`_.
- `The imagenode program that captures and sends images <https://github.com/jeffbass/imagezmq>`_.
- `The larger farm automation / computer vision project <https://github.com/jeffbass/yin-yang-ranch>`_.
  This project also shows the overall system architecture.

Contributing
============
**imagehub** is in early development and testing. I welcome open issues and
pull requests, but because the code is still rapidly evolving, it is best
to open an issue with some discussion before submitting any pull requests or
code changes.

Acknowledgments
===============
- **ZeroMQ** is a great messaging library with great documentation
  at `ZeroMQ.org <http://zeromq.org/>`_.
- **PyZMQ** serialization examples provided a starting point for **imagezmq**.
  See the
  `PyZMQ documentation <https://pyzmq.readthedocs.io/en/latest/index.html>`_.
