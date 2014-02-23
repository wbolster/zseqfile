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

* gzip (`.gz`) using built-in module, `gzip`, or `pigz`
* bzip2 (`.bz2`) using built-in module, `bzip2`, or `pbzip2`
* xz  (`.xz`) using built-in module, `xz`


Currently implemented
=====================

* Basic reading support
  
* `open_gzip()`, `open_bzip2()`, `open_lzma()` that can either use the
  built-in Python modules, or delegate to external processes (including the
  parallelized programs).

* A `.open()` function that delegates to the right `open_*()` function based
  on the file name.


Issues, notes, todo, ideas
==========================

* Writing support is not yet implemented

* Only Python >= 3.3 is currently supported. Backporting only after this
  project has matured a bit more.

* For external processes, only "real files" are supported (those with a
  `.fileno()`, custom "file like objects" are not.

* The `lzma` module is only available from the standard library since Python
  3.3.

* How to set compression options (e.g. ``-9``) using a clean API?

* Maybe support appending to compressed files; this works with the gzip, bz2
  and xz file formats (multiple streams in a single file), but support in
  stdlib modules is incomplete.

* Maybe add "magical" file discovery by trying to open the file using a name
  with an added extension?

* Support usage as context manager in all cases, even if the stdlib doesn't
  support it in all cases for the built-in modules in older Python version.
