=========================================
imagehub Research and Development Roadmap
=========================================

Overview
--------

**imagehub** is constantly evolving. It is a "science project" that is part of
a larger system to observe, monitor and optimize a small permaculture farm. It
is part of a distributed computer vision and sensor network. Here is where I
keep the list of the stuff I'm experimenting with but haven't pushed to GitHub
yet. Feel free to open an issue and make suggestions or start a discussion
about a potential change or new feature. The list below is not in any particular
order; all of these are ongoing experiments on differing timelines.

.. contents::

Receive and send along commands or requests to imagenode from Librarian
-----------------------------------------------------------------------
Right now, the **imagehub** returns "OK" after every message tuple is sent. The
reply can be a "command word" instead that would cause **imagenode** to take
an action such as change the exposure_mode of the PiCamera. Or send a dozen
"live frames" from the camera (even though no detector has activated). Command
words look like this (format is: CommandWord value):
- OK  # that is the only one now and is sent back for every reply.
- ReloadYaml  # reload the yaml file to get a change in one of the options.
- SendFrames 10  # Send some frames now, even if no detector is activated.
- SetResolution (640,480)  # set a new resolution value for the camera.

Command words would arrive from the Librarian and be sent to the specific
**imagenode** that is mentioned in the command.

Add additional logic to handle commands and requests from Librarian
-------------------------------------------------------------------
Currently, all event message, images and heartbeat messages originate from
**imagenodes**. Event messages are logged, images are saved and heartbeat
messages get a reply but cause no action on the part of the **imagehub**.
Additional logic needs to be added to receive command and request messages
from the Librarian. They will have the same message tuple format, but will
need to be handled using added logic in process() method.

`Return to main documentation page README.rst <../README.rst>`_
