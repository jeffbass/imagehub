"""imagehub: receive and save images and events from imagenodes

Receives and stores event messages and event images from multiple
sources simultaneously. The sources are Raspberry Pi (and other) computers
running imaganode.py to capture and send selected images and event messages.

Typically run as a service or background process. See README.rst for details.

Copyright (c) 2018 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""
# populate fields for >>>help(imagezmq)
from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__
