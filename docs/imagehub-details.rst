==============================================================
How **imagehub** works: pseudo code and data structure design
==============================================================

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

Event messages look like this (there is also a small black image as 2nd part of
each message tuple, not shown here)::
  WaterMeter|startup|
  WaterMeter|OK|                 # If Heartbeat message option chosen
  WaterMeter|motion|moving
  WaterMeter|motion|still
  Garage|light|lighted
  Garage|light|dark
  JeffOffice window|light|lighted
  JeffOffice door|motion|still

The template for **event** messages is::
  node name and view name|information|detected state

For each **event** message received, the date / time is added and the message
is added to the event log using Python's logging module. The log files grow
to a set size (set by option ``log_max_size``) and then rotate, creating imagehub.log,
imagehug.log.1, imagehub.log2, etc.

Image messages look like this (the image itself is the 2nd part of each
message tuple, not shown here)::
  WaterMeter|jpg|moving
  WaterMeter|image|moving
  Garage|jpg|lighted
  Garage|image|lighted

The template for **image** messages is::
    node name and view name|send_type|detector state

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
      ├── imagehub.log     # contains the most recent event messages
      ├── imagehub.log.1   # ...contains earlier event messages
      ├── imagehub.log.2   # ...contains even earlier event messages
      └──  # etc, etc.


`Return to main documentation page README.rst <../README.rst>`_
