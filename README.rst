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
are handled by other programs. See `Using imagenode in distributed computer vision projects <https://github.com/jeffbass/imagenode/blob/master/docs/imagenode-uses.rst>`_
for a more detailed explanation of the overall project design. See the
`Yin Yang Ranch project <https://github.com/jeffbass/yin-yang-ranch>`_
for more details about the architecture of the
**imagenode** <--> **imageZMQ** <--> **imagehub** system.


imagehub Features
=================

- Receives and save images from multiple Raspberry Pi's simultaneously.
- Receives and logs event messages from multiple RPi's simultaneously.
- Uses threading for image writing to enhance responsiveness.
- Threading can be replaced with multiprocessing with minimal code changes.

Dependencies and Installation
=============================

**imagehub** has been tested with:

- Python 3.5, 3.6 and 3.7
- OpenCV 3.3 and 4.0+
- PyZMQ 16.0+
- imageZMQ 1.0.1+

**imagehub** uses **imageZMQ** to receive event messages and images that are
captured and sent by **imagenode**. You will need to install and test both
**imageZMQ** and **imagenode** before using **imagehub**.
The instructions for installing and testing **imageZMQ** are in the
`imageZMQ GitHub repository <https://github.com/jeffbass/imagezmq.git>`_.
The instructions for installing and testing **imagenode** are in the
`imagenode GitHub repository <https://github.com/jeffbass/imagenode.git>`_.

**imagehub** is still in early development, so it is not yet in PyPI. Get it by
cloning the GitHub repository::

    git clone https://github.com/jeffbass/imagehub.git

Once you have cloned **imagehub** to a directory on your local machine,
you can run the tests using the instructions below. The instructions assume you
have cloned both **imagehub** to the user home directory. It
is also important that you have successfully run all the tests for **imageZMQ**
and for **imagenode**. The recommended testing arrangement is to run **imagehub**
on the same Mac (or other display computer) that you used to run the
``imagezmq/tests/timing_receive_jpg_buf.py`` program when you tested **imagenode**.

Running the Tests
=================

**imagehub** should be tested after you have tested **imagenode**, because you
will be using **imagenode** to send test images and event messages to
**imagehub**.

Both **imagehub** and **imagenode** use **imageZMQ** for sending and receiving
images and event messages. The **imageZMQ** package is pip installable. It is
likely that you already have it installed from your tests of **imagenode**. If
not, it should be pip installed in a virtual environment. For example,
my virtual environment is named **py3cv3**.

To install **imageZMQ** using pip:

.. code-block:: bash

    workon py3cv3  # use your own virtual environment name
    pip install imagezmq


Test **imagehub** in the same virtualenv that you installed **imagenZMQ** in.
For **imageZMQ** and **imagenode** testing, my virtualenv is called ``py3cv3``.

To test **imagehub**, you will use the same setup as Test 2 for **imagenode**.
You will run **imagenode** on a Raspberry Pi with a PiCamera, just as you did for
**imagenode** Test 2. You will run **imagehub** on the same Mac (or other display
computer) that you used to display the **imagenode** test images.

Directory Structure for running the imagehub tests
--------------------------------------------------
Neither **imagehub** or **imagenode** are far enough along in their development
to be pip installable. So they should both be git-cloned to the computers that
they will each be running on. I recommend doing all testing in the user home
directory. Here is a simplified directory layout for the computer that will be
running **imagehub**::

  ~ # user home directory of the computer running imagehub
  +--- imagehub.yaml  # copied from imagenode/imagenode.yaml in this repository
  |
  +--- imagehub    # the git-cloned directory for imagehub
  |    +--- sub directories include docs, imagehub, tests
  |
  +--- imagehub_data   # this directory will be created by imagehub
      +--- images      # images will be saved here
      +--- logs        # logs containing event messages will be saved here

The **imagehub** directory arrangement, including docs, **imagehub** code,
tests, etc. is a common software development directory arrangement on GitHub.
Using ``git clone`` from your user home directory on your **imagehub** computer
(either on a Mac, a RPi or other Linux computer) will put the **imagehub**
directories in the right place for testing. When the **imagehub** program runs,
it creates a directory (``imagehub_data``) with 2 subdirectories (``images`` and
``logs``) to store the images and event messages it receives from **imagenode**
running on one or more RPi's or other computers. Running **imagenode** requires
a settings file named ``imagehub.yaml``. To run the tests, copy the example
``imagehub.yaml`` file from the ``imagehub`` directory to your home directory.
The ``imagehub.yaml`` settings file is expected to be in your home directory,
but you can specify another directory path using the --path optional argument.
I recommend putting the ``imagehub.yaml`` file in your home directory for
testing. You can move the ``imagehub.yaml`` file to a different directory after
you have completed the tests.

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
is helpful for testing, but not for production runs. I use systemctl / systemd
to start **imagehub** in production. I have provided an example
``imagehub.service`` unit configuration file that shows how I start **imagehub**
for the production programs observing my small farm. I have found the systemctl
/ systemd system to be best way to start / stop / restart and check status of
**imagehub** over several years of testing. For those who prefer using a shell
script to start **imagehub**, I have included an example ``imagehub.sh``. It is
important to run **imagehub** in the right virtualenv in production, regardless
of your choice of program startup tools.

In production, you would want to set the test options used to print settings
to ``False``; they are only helpful during testing. All errors and **imagenode**
event messages are saved in the file ``imagehub.log`` which is located in the
directory you specify in the ``imagenode.yaml`` setting ``data_directory``:

.. code-block:: yaml

    data_directory: imagehub_data

The ``imagehub.yaml`` settings file is expected to be in the users home
directory by default. You can specify the path to a different directory
containing ``imagehub.yaml`` by using the optional argument ``--path``:

.. code-block:: bash

    workon py3cv3  # use your own virtual environment name
    python3 imagenode.py --path directory_name  # directory holding imagehub.yaml

Additional Documentation
========================
- `How imagehub works <docs/imagehub-details.rst>`_.
- `The imagehub Settings and the imagehub.yaml file <docs/settings-yaml.rst>`_.
- `Version History and Changelog <HISTORY.md>`_.
- `Research and Development Roadmap <docs/research-roadmap.rst>`_.
- `The imageZMQ classes that allow transfer of images <https://github.com/jeffbass/imagezmq>`_.
- `The imagenode program that captures and sends images <https://github.com/jeffbass/imagenode>`_.
- `The larger farm automation / computer vision project <https://github.com/jeffbass/yin-yang-ranch>`_.
  This project shows the overall system architecture. It also contains
  links to my **PyCon 2020** talk video and slides explaining the project.

Contributing
============
**imagehub** is in early development and testing. I welcome open issues and
pull requests, but because the code is still rapidly evolving, it is best
to open an issue with some discussion before submitting any pull requests or
code changes.  We can exchange ideas about your potential pull request and how
to best incorporate and test your code.

Acknowledgments
===============
- **ZeroMQ** is a great messaging library with great documentation
  at `ZeroMQ.org <http://zeromq.org/>`_.
- **PyZMQ** serialization examples provided a starting point for **imageZMQ**.
  See the
  `PyZMQ documentation <https://pyzmq.readthedocs.io/en/latest/index.html>`_.
