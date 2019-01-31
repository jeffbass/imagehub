====================================
imagehub Release and Version History
====================================

Overview
--------

**imagehub** is constantly evolving. Release and Version History is tracked
here, with the most recent changes at the top.

.. contents::

0.1.0  (2019-01-30)
-------------------
- Added Release and Version History.
- Added Research and Development Roadmap.
- Added a check for "send_test_image" images from **imagenode**. Now returns
  without saving the "send_test_image" images. Caused an index out of range
  error before.

0.0.2  (2019-01-05)
-------------------
- Moved image writing to a thread to speed up image message receive loop.
- Bug Fixes:

  - Fixed index out of range on message[1].split.
  - Fixed a number of documentation broken links and formatting errors.

0.0.1  (2018-11-12)
-------------------
- First commit; major refactor after 18 months of testing previous version.
- Includes hub receipt and saving of images and event messages from **imagenodes**.

`Return to main documentation page README.rst <../README.rst>`_
