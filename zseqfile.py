"""
zseqfile - transparently handle compressed files
"""

import bz2
import gzip
import io
import lzma
import os


#
# Helper functions
#

def is_executable_file(path):
    """Check whether the specified path is an executable file."""
    return os.path.isfile(path) and os.access(path, os.X_OK)


def which(executable):
    """Return the path to the specified executable, or None if not found."""

    # Absolute paths
    if os.path.isabs(executable):
        if is_executable_file(executable):
            return executable
        else:
            return None

    # Search $PATH
    for dir in os.environ.get('PATH', '').split(os.pathsep):
        file = os.path.join(dir, executable)
        if is_executable_file(file):
            return file

    # Not found
    return None


def open_regular(file, mode, encoding, errors, newline):
    return io.open(file, mode=mode, encoding=encoding, errors=errors,
                   newline=newline)


def open_gzip(file, mode, encoding, errors, newline):
    return gzip.open(file, mode=mode, encoding=encoding, errors=errors,
                     newline=newline)


def open_bzip2(file, mode, encoding, errors, newline):
    return bz2.open(file, mode=mode, encoding=encoding, errors=errors,
                    newline=newline)


def open_lzma(file, mode, encoding, errors, newline):
    return lzma.open(file, mode=mode, encoding=encoding, errors=errors,
                     newline=newline)


SUFFIX_MAP = {
    '.gz': open_gzip,
    '.bz2': open_bzip2,
    '.xz': open_lzma,
    '.lzma': open_lzma,
}


#
# Public API
#

def open(file, mode='r', encoding=None, errors=None, newline=None):

    opener = open_regular
    for suffix, func in SUFFIX_MAP.items():
        if file.endswith(suffix):
            opener = func

    return opener(file, mode, encoding, errors, newline)
