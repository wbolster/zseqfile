========
zseqfile
========

.. warning::

   This software is alpha quality and not ready for general use!


*zseqfile* is a Python library to simplify sequential access to compressed
files, either for reading or writing.

It can optionally use external programs for compression/decompression, which
might increase performance if you have multiple CPUs (or CPU cores).

The supported compression formats are:

* gzip (`.gz`)
* bzip2 (`.bz2`)
* xz  (`.xz`)
* lzma (`.lzma`)


Issues, notes, ideas
====================

* Only Python >= 3.3 is currently supported

* Only "real files" on disk are supported, "file like objects" are not.

* The `lzma` module is only available from the standard library since Python
  3.3.

* How to set compression options (e.g. ``-9``) using a clean API?

* Maybe support appending to compressed files; this works with the gzip, bz2 and
  xz file formats (multiple streams in a single file), but support in stdlib
  modules is incomplete.

* Maybe add "magical" file discovery by trying to open the file using a name
  with an added extension?
