# Version History and Changelog

All notable changes the **imagehub** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Ongoing Development

- Improving documentation content, layout, arrangement and flow.
- Developing a "large image buffer" using the new Python 3.8 SharedMemory
  class. The idea: put all newly received images into a very
  large (up to available memory; could be 3GB or more). This would allow
  receiving images into this buffer and then immediately returning the 'OK'
  message back to the sending **imagenode**. Then a separate `multiprocessing`
  process empties the buffer by saving images in a separate process. The
  theoretical advantage over the existing setup (saving images in a separate
  thread) would be that a 2nd process (on a different CPU core) for saving
  images could be much faster than a thread running on the same core. Early
  tests are promising, but the speed versus complexity tradeoffs aren't clear
  yet.

## 0.2.0 - 2021-01-17

### Improvements

- Changed the file naming convention for the saved event messages by using the
  TimedRotatingFileHandler in event logging.
- Reorganized previous docs/release-history.rst into this more standardized
  HISTORY.md file.
- Updated Research and Development Roadmap.

### Changes and Bugfixes

- Multiple fixes to all documentation files.

## 0.1.0 - 2019-01-30

### Improvements

- Added Release and Version History.
- Added Research and Development Roadmap.

### Changes and Bugfixes

- Added a check for "send_test_image" images sent from **imagenode**. No longer
  saves the "send_test_image" images. Caused an index out of range error before.
- Multiple fixes to all documentation files.

## 0.0.2 - 2019-01-05

### Improvements

- Moved image writing to a thread to speed up image message receive loop.

### Changes and Bugfixes

- Fixed index out of range on message[1].split.
- Fixed a number of documentation broken links and formatting errors.

## 0.0.1 - 2018-11-12

- First commit to GitHub
- Major refactoring after 18 months of testing previous version.
- Includes receipt and saving of images and event messages from **imagenodes**,
  but no threading for saving images.


[Return to main documentation page README](README.rst)
