==================================================================
Testing **imagehub** with Raspberry Pi **imagenode** image sources
==================================================================

.. contents::

Overview
========

**imagehub** is a part of a distributed computer vision system that runs
on multiple computers. The minimal system is one Raspberry Pi running
**imagenode** and one larger computer (such as a Mac) running **imagehub**.
You can see the overall design of such a system in the yin-yang-ranch
Github repository  `Yin Yang Ranch project <https://github.com/jeffbass/yin-yang-ranch>`_.
**imagehub** is dependent on having working copies of **imagezmq** on both the
RPi computer and the display computer. Be sure to set up and test both
**imagezmq** and **imagenode**
BEFORE you try to install and test **imagehub**. The instructions for
installing and testing **imagezmq** are in the
`imagezmq GitHub repository <https://github.com/jeffbass/imagezmq.git>`_.
The instructions for
installing and testing **imagenode** are in the
`imagenode GitHub repository <https://github.com/jeffbass/imagenode.git>`_.

Running the tests below will place 3 new directories on the computer running
**imagenode**: (1) a ``logs`` directory, (2) an ``images`` directory and (3)
an ``imagehub_data`` directory. This last directory can be changed by changing
the ``data_directory`` option in the the ``imagehub.yaml`` file.

Directory Structure for the Tests
=================================
Both **imagehub** and **imagezmq** should be git-cloned to the computer
that they will be running on. I have done all testing at the user home
directory::

  ~  # user home directory
  +--- imagehub.yaml  # copied from example.yaml file & edited as needed
  |
  +--- imagehub    # the git-cloned directory for imagehub
  |    +--- docs
  |    +--- imagehub
  |         +--- imagehub.py
  |
  +--- imagezmq   # the git-cloned directory for imagezmq
       +--- docs
       +--- imagezmq
       |    +--- imagezmq.py  # contains the imagezmq classes
       +--- tests
            +--- timing_receive_jpg_buf.py
            +--- ...etc, etc.


Test 1: Running **imagehub** with a single **imagenode** sender
===============================================================
**The first test** runs the sending program **imagenode** on an RPi and the
receiving program **imagehub** on a mac (typically the same one you used
as a display computer when you tested **imagenode**).

1. Clone the **imagenode** GitHub repository onto your mac in your home
   directory::

     git clone https://github.com/jeffbass/imagehub.git

3. Open 2 terminal windows on your Mac. One will be used for running
   **imagehub** and the other will be used for running **imagenode** on
   a Raspberry Pi.

4. In one terminal window, copy ``imagehub/imagehub.yaml`` to ``imagehub.yaml``
   in the home directory (~) using the command below. You will not need to
   edit the yaml file. The name of the file in the home directory must be
   ``imagehub.yaml`` for this test::

     cp  ~/imagehub/imagehub.yaml  ~/imagehub.yaml

5. In the same terminal window, change to the ``~/imagehub/imagehub`` directory.
   You will be running imagehub.py from here in a few more steps::

     cd ~/imagehub/imagehub

6. In the same terminal window, run the program ``imagehub.py``
   and leave it running::

    workon py3cv3  # my virtualenv name; use yours instead
    python imagehub.py

7. In the other terminal window, log in to the Raspberry Pi that you will be
   using to run **imagenode**. This will probalby be the same Raspberry Pi that
   you tested **imagenode** on. Change to the **imagenode** program directory
   and run the **imagenode** program as you did during testing. NOTE: You
   will want to change the "send_frames" option in the ~/imagenode.yaml file on
   the Raspberry Pi to "detected event", or else you will save thousands of
   images that will be sent if the "send_frames" option is set to "continuous"
   as it was when you tested **imagenode**::

     cd ~/imagenode/imagenode
     python imagenode.py

8. Move something or change the lighting in the ROI area of the **imagenode**
   PiCamera. When you tested **imagenode** using an **imagezmq** test program as
   a hub you created motion or changed lighting. Do the same for this test.

9. You won't see anything happen...remember, all that **imagehub** does is
   receive and save the event messages and images being sent by **imagenode**.
   So, after a few minutes of "creating events" in front of the camera, you can
   stop both programs by pressing Ctrl-C in both terminal windows.

If you look in the ``imagehub_data`` directory you will see some files that
contain the event messages from your imagenode PiCamera. They will appear like
this::

  ~/imagehub_data
  ├── images
  │   └─── 2018-12-30  # this will be named for the date of your testing
  │       ├── YourNodeName-2018-12-30T23.13.31.620992.jpg
  │       ├── YourNodeName-2018-12-30T23.13.31.813029.jpg
  │       └──  # etc, etc. for additional images
  │
  └── logs
      └─── imagehub.log  # contains event messages created by your testing

Images created by your motion or light changes will be named according to your
node "name" option in the ~/imagenode.yaml file on the Raspbery Pi. You can use
any image viewer to look at these jpg images.

If you view the imagehub.log file, you will see an event listing that looks like
the log example in the beginning of the README.rst file.

Remember, when running the tests, start the **imagehub** program running first,
and then start the **imagenode** program. You can end the programs by pressing
Ctrl-C in each terminal window.

Test 2: Running **imagehub** with 2 **imagenode** senders simultaneously
========================================================================

**The second test** should be run with 2 Raspberry Pi's running **imagenode**,
with both of them simultaneously sending event messages and images to **imagehub**.
Run this test the same way as Test 1, but open a third terminal window in which
to start **imagenode** running on a 2nd Raspberry Pi with a PiCamera.

1. In one terminal window on the Mac, start the **imagehub** program running.
2. In a second terminal window on the Mac, ssh into one of the Raspberry Pi
   computers and start **imagenode**.
3. In a third terminal window on the Mac, ssh into a different Raspberry Pi
   computer and start **imagenode**.
4. Make motion or light changes in front of the PiCameras to create events.

The images and log items saved by this test will add cumulatively to the ones
saved in Test 1, so you will see all the images from Test 1 AND all the images
from Test 2 in the images directory. And the event messages in the log will be
added to the ones put into the log during Test 1.

It is important that the node "name" option specify a DIFFERENT node name for each
of Raspberry Pi (in the ~/imagenode.yaml file on each RPi). The node name
becomes part of the file name of each image and it labels each event in the log.

There are a few settings in the imagehub.yaml file that specify the data
directory, a maximum number of images to write, etc. You can learn more about
these options in `ImageHub Settings and the imagehub.yaml file <docs/settings-yaml.rst>`_.

`Return to main documentation page README.rst <../README.rst>`_
