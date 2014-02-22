"""
zseqfile - transparently handle compressed files
"""

# Expose the public API.
from .zseqfile import (  # noqa
    open,
    open_gzip,
    open_bzip2,
    open_lzma,
)
