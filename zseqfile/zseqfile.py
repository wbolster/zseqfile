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


def make_process_wrapper(args, mode, encoding, errors, newline):
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    # FIXME: properly terminate the process when .close() is called

    if 't' in mode:
        return io.TextIOWrapper(process.stdout, encoding, errors, newline)
    else:
        return process.stdout


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
    assert EXTERNAL_GZIP
    return make_process_wrapper(
        [EXTERNAL_GZIP, '-c', '-d', file],
        mode, encoding, errors, newline)


def open_external_pigz(file, mode, encoding, errors, newline):
    assert EXTERNAL_PIGZ
    return make_process_wrapper(
        [EXTERNAL_PIGZ, '-c', '-d', file],
        mode, encoding, errors, newline)


def open_gzip(file, mode, encoding, errors, newline, external, parallel):
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
    assert EXTERNAL_BZIP2
    return make_process_wrapper(
        [EXTERNAL_BZIP2, '-c', '-d', file],
        mode, encoding, errors, newline)


def open_external_pbzip2(file, mode, encoding, errors, newline):
    assert EXTERNAL_PBZIP2
    return make_process_wrapper(
        [EXTERNAL_PBZIP2, '-c', '-d', file],
        mode, encoding, errors, newline)


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
    assert EXTERNAL_XZ
    return make_process_wrapper(
        [EXTERNAL_XZ, '-c', '-d', file],
        mode, encoding, errors, newline)


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

    return opener(file, mode, encoding, errors, newline, external, parallel)
