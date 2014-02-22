"""
zseqfile - transparently handle compressed files
"""

from .zseqfile import (  # noqa
    open,
    open_gzip,
    open_bzip2,
    open_lzma,
)

open_gz = open_gzip
open_bz2 = open_bzip2
open_xz = open_lzma
