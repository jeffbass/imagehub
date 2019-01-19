============================================
ImageHub Settings and the imagehub.yaml file
============================================

.. contents::

========
Overview
========

Here is the imagehub.yaml file where all the options have been specified::

  # Settings file imagehub.yaml -- example with all settings
  ---
  hub:
    queuemax: 500 # maximum size of the memory queue of images to write
    patience: 68  # how many minutes before logging a "no messages" event
    print_settings: False
    data_directory: imagehub_data
    max_images_write: 9000 # a cap on images to write in one day

=============================
YAML file names and locations
=============================

The **imagenode** program expects its settings to be in a file named
``imagenode.yaml`` in the home directory.

There is an example ``imagehub.yaml`` file in the main repository folder. It is
the same as the file shown above. To use the file, copy it to the home
directory and edit it there. That way you can keep the example file unchanged
for future reference.

The **imagehub** list of options is much smaller than the **imagenode** list.

Conventions used for settings
=============================

Settings follow YAML conventions. The settings are dictionary key value pairs.
For example::

  queuemax: 500

The example ``imagehub.yaml`` file shows how the settings are arranged. There is no error
checking of the settings; if a setting is not set to an expected value, then
a Python traceback error will result. This is adequate for debugging issues
with settings (misspelling a setting name, etc.) and saves writing a lot of
deeply nested if statements. You can also specify an option in the settings
to print the settings; this can be helpful in spotting option misspellings, etc.

==================================
ImageHub Settings in the YAML file
==================================

There are 5 optional settings available::

  queuemax: 500 # maximum size of the memory queue of images to write
  patience: 5  # how many minutes before logging a "no messages" event
  data_directory: imagehub_data
  max_images_write: 9000 # a cap on images to write in one day
  print_settings: False

The ``queuemax`` option sets a size on the image writing queue in memory. If
not specified, the default is 500. You will only need to specify a smaller
number if you are running out of memory.

The ``patience`` setting sets the maximum number of minutes for **imagehub**
to wait for an event reported by a sending **imagenode**. If there has been no
event or image received in in that number of minutes, a "no messages received"
event will be placed in the log. This is helpful for debugging communications
issues, which are usually caused by an incorrect hub address specified by
an **imagenode**. Exceeding the ``patience`` time will not end the program, it
will just put an event into the log after the specified amount of time.

The ``data_directory`` setting sets the name of the directory where the images and
event logs will be stored. The default is ``imagehub_data`` in the home directory.

The ``max_images_write`` option is a "safety" option to prevent filling a disk
with unintended images. For example, if an imagenode is (unintentionally) set
to send images option ``continuous``, then the number of images received and
saved could rapidly fill a disk drive on the hub. I know this from a my own
bad experience when I forgot to change the ``continuous`` option to ``detected
event`` on one of my RPi nodes.

The ``max_images_write`` option is the most important option and the most difficult
to explain. **imagehub** logic starts a new directory each time the date changes.
So, the max_images_write parameter is set to 0 each time a new directory is
created. And the image_count in incremented each time an image is written. When
image_count exceeds ``max_images_write``, there is no more writing in that directory.
Writing resumes when a new directory is created (normally when the date changes).
The default is 9000 if you don't specify an option.

The ``print_settings`` option allows you to print the options that were read
by the **imagehub** program to check spelling etc. The default is ``False``.

`Return to main documentation page README.rst <../README.rst>`_
