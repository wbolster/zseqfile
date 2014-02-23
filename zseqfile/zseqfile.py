import bz2
import gzip
import io
import lzma
import os
import subprocess


SUPPORTED_MODES = {'rt', 'rb', 'wt', 'wb'}


#
# Helpers
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


EXTERNAL_GZIP = which('gzip')
EXTERNAL_PIGZ = which('pigz')
EXTERNAL_BZIP2 = which('bzip2')
EXTERNAL_PBZIP2 = which('pbzip2')
EXTERNAL_XZ = which('xz')


class ProcessIOBase(object):
    """
    Shared functionality for the reader and writer classes.
    """
    def close(self):
        if self._closed:
            return

        if self._should_close:
            self._fp.close()

        self._pipe.close()
        self._process.terminate()
        self._process.wait()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


class ProcessIOReader(ProcessIOBase):
    """
    Readable file-like object that wraps an external process.
    """
    def __init__(self, args, file, mode, encoding=None, errors=None,
                 newline=None):
        assert mode in SUPPORTED_MODES
        assert 'r' in mode

        self._closed = False

        if isinstance(file, str):
            self._fp = io.open(file, mode='rb')
            self._should_close = True
        else:
            self._fp = file
            self._should_close = False

        self._process = subprocess.Popen(
            args,
            stdin=self._fp,
            stdout=subprocess.PIPE)
        self._pipe = self._process.stdout

        if 't' in mode:
            self._pipe = io.TextIOWrapper(
                self._pipe,
                encoding=encoding,
                errors=errors,
                newline=newline)

        # Expose API. TODO: Maybe add real stub methofs for these for
        # documentation purposes.
        self.readable = self._pipe.readable
        self.read = self._pipe.read
        self.readline = self._pipe.readline
        self.readlines = self._pipe.readlines

    def __iter__(self):
        return iter(self._pipe)


class ProcessIOWriter(ProcessIOBase):
    """
    Writable file-like object that wraps an external process.
    """
    def __init__(self, args, file, mode, encoding=None, errors=None,
                 newline=None):
        raise NotImplementedError()


#
# Uncompressed files
#

def open_regular(file, mode, encoding, errors, newline, external, parallel):
    # Simply ignore 'external' and 'parallel' args
    return io.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# Gzip
#

def open_external_gzip(file, mode, encoding, errors, newline):
    args = [EXTERNAL_GZIP, '-c', '-d']
    return ProcessIOReader(args, file, mode, encoding, errors, newline)


def open_external_pigz(file, mode, encoding, errors, newline):
    args = [EXTERNAL_PIGZ, '-c', '-d']
    return ProcessIOReader(args, file, mode, encoding, errors, newline)


def open_gzip(file, *, mode, encoding=None, errors=None, newline=None,
              external=False, parallel=False):
    if external:
        if parallel and EXTERNAL_PIGZ:
            return open_external_pigz(file, mode, encoding, errors, newline)

        if EXTERNAL_GZIP:
            return open_external_gzip(file, mode, encoding, errors, newline)

    return gzip.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# Bzip2
#

def open_external_bzip2(file, mode, encoding, errors, newline):
    args = [EXTERNAL_BZIP2, '-c', '-d']
    return ProcessIOReader(args, file, mode, encoding, errors, newline)


def open_external_pbzip2(file, mode, encoding, errors, newline):
    args = [EXTERNAL_PBZIP2, '-c', '-d']
    return ProcessIOReader(args, file, mode, encoding, errors, newline)


def open_bzip2(file, mode, encoding, errors, newline, external, parallel):
    if external:
        if parallel and EXTERNAL_PBZIP2:
            return open_external_pbzip2(file, mode, encoding, errors, newline)

        if EXTERNAL_BZIP2:
            return open_external_bzip2(file, mode, encoding, errors, newline)

    return bz2.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# XZ/LZMA
#

def open_external_xz(file, mode, encoding, errors, newline):
    args = [EXTERNAL_XZ, '-c', '-d']
    return ProcessIOReader(args, file, mode, encoding, errors, newline)


def open_lzma(file, mode, encoding, errors, newline, external, parallel):
    if external and EXTERNAL_XZ:
        return open_external_xz(file, mode, encoding, errors, newline)

    return lzma.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# Magic open() API
#

SUFFIX_MAP = {
    '.gz': open_gzip,
    '.bz2': open_bzip2,
    '.xz': open_lzma,
    '.lzma': open_lzma,
}


def open(file, mode='rt', *, encoding=None, errors=None, newline=None,
         external=False, parallel=False):

    if mode not in SUPPORTED_MODES:
        msg = "Unsupported mode {!r}, must be one of {}"
        raise ValueError(msg.format(mode, ", ".join(sorted(SUPPORTED_MODES))))

    opener = open_regular
    for suffix, func in SUFFIX_MAP.items():
        if file.endswith(suffix):
            opener = func

    return opener(file, mode=mode, encoding=encoding, errors=errors,
                  newline=newline, external=external, parallel=parallel)
