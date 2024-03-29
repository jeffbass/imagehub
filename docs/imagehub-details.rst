======================================================
How **imagehub** works: pseudo code and data structure
======================================================

Imagenode sets up an imagezmq hub and waits to hear from imagenodes. When it
receives an imagenode message, it files it by node name, date and time. It saves
received images in image directories, with one directory per calendar date. It
records event messages in an event log, organizing them by date node name.

In pseudo code, here's what **imagehub** does::

  # stuff done one time at program startup
  Read a YAML file into Settings (e.g. what directory to store data)
  Start the Hub Events Log
  Instantiate a Hub using Settings and activate an imagezmq hub

  # stuff done to receive and process each incoming message
  Loop forever:
    Receive a message tuple from any imagenode labelled by node name
      If it is an event message, add it to the log
      If it is an image, add it to the appropriate image directory
      Send 'OK' reply to imagenode indicating message received

Here are the classes and data structures::

  Class Settings (filled once by reading from the YAML file)
  Class ImageHub (instantiated once using Settings)
  Class HealthMonitor (methods for helping monitory system and network health)

The ``ImageHub`` class contains methods to make image directories, save image
files and add event messages to the log.

The ``HealthMonitor`` class is pretty simple so far. It determines what
kind of computer **imagenode** is running on so that the right camera, sensor
and light control libraries can be imported. It also holds the methods to
implement ``heartbeat`` messages to help maintain network reliablity. You can
read more about the ``HealthMonitor`` class in the
`HealthMonitor documentation <nodehealth.rst>`_.

In essence, the **imagenode** program runs one or more cameras and sends a
highly selective stream of images and status messages to the **imagehub**.
The **imagehub** stores the messages in event logs and stores the images in
image history directories.

Messaging protocol for images and status messages
=================================================

By design, every message passed by an **imagenode** to the **imagehub**
has a specific format. Every message is sent using **imagezmq** and
is a tuple::

  (text, image)

There are 2 categories of messages: (1) event messages that are text (with no
image from a camera), and (2) images from a camera.

**Event messages** are about detected events, such as "lighted" or "dark". For
event messages, the image portion of the tuple is a tiny black image. This
allows all messages to have the same tuple layout.

**Image messages** have identifying information (like node name, view name, etc.)
in the text portion of the tuple, and the image itself (or jpeg version of the
image) in the image portion of the tuple.

In both message types, the "|" character is used as a field delimiter. If there
is only one camera, then the view name could be absent.

**Event messages** look like this (there is also a small black image as 2nd part
of each message tuple, not shown here)::
  JeffOffice|Restart|rpi99|RPi|192.168.86.38|859|149.48
  JeffOffice|Temp|77 F
  WaterMeter|motion|moving
  WaterMeter|motion|still
  Garage|light|lighted
  Garage|light|dark
  Garage|Temp|76 F
  BackDeck|Temp|98 F
  Barn|motion|moving
  Barn|motion|still
  Driveway Mailbox|motion|moving
  Driveway Mailbox|motion|still
  Driveway|Restart|rpi20|RPi|192.168.86.52|875|738.71
  Driveway Mailbox|motion|still
  Driveway|Temp|98 F

The template for **event** messages is::

  node name and view name|event type|detected state or other information

The ``view name`` is optional and is used when there are 2 different
cameras attached to an imagenode. The ``node name`` is always present, even when
a ``view name`` is not. For example, the Driveway imagenode shown above has a
camera with a view toward the Mailbox. The ``Mailbox`` view name appears when a
motion event occurs but is not present when non-camera events occur, such as the
restart of an imagenode or an imagenode sensor temperature reading.

For each **event** message received, the date / time is added and the message
is added to the event log using Python's logging module. The log files are
rotated each day at midnight, creating ``imagehub.log, imagehug.log.2020.12.25,
imagehub.log.2020.12.24``, etc. In this pattern, today's event messages are
always in the file ``imagehub.log``. And all previous event messages are in a
log file that ends in the date they were logged. The log naming pattern is
provided by the ``TimedRotatingFileHandler`` of Python's ``logging`` module.

**Image messages** look like this (the image itself is the 2nd part of each
message tuple, not shown here)::
  WaterMeter|jpg|moving
  WaterMeter|image|moving
  Garage|jpg|lighted
  Garage|image|lighted

The template for **image** messages is::

    node name and view name|send_type|detector state

The ``view name`` is optional and is used when there are 2 different
cameras attached to an imagenode. The ``node name`` is always present, even when
a ``view name`` is not. The ``send_type`` is the type of image file that has
been sent. Current choices are ``jpg`` for JPEG compressed images or ``image``
for OpenCV images in their native (uncompressed) state as a Numpy array.

When **imagehub** receives an image message as formatted above, it adds the date and
time to the nodename and saves the image in the images directory. The images
directory is organized by date, so the final data directory and file structure
looks like this::

  imagehub_data
  ├── images
  │   ├── 2018-12-30
  │   │   ├── Barn-2018-12-30T23.13.31.620992.jpg
  │   │   ├── WaterMeter-2018-12-30T23.08.35.151117.jpg
  │   │   └──  # etc, etc. for additional images
  │   ├── 2018-12-05
  │   │   ├── Barn-2018-12-31T15.07.47.378240.jpg
  │   │   ├── WaterMeter-2018-12-31T15.09.45.610104.jpg
  │   │   ├── WaterMeter-2018-12-31T15.09.45.847916.jpg
  │   │   └──  # etc, etc. for additional images
  │   │
  │   └──  # additional directories for each date
  │
  └── logs
      ├── imagehub.log     # contains the most recent (today) event messages
      ├── imagehub.log.2020.12.25   # ...contains previous day event messages
      ├── imagehub.log.2020.12.24   # ...contains previous day event messages
      └──  # etc, etc.


`Return to main documentation page README.rst <../README.rst>`_
