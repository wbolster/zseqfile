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


def make_process_wrapper(args, mode, encoding, errors, newline):
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    # FIXME: properly terminate the process when .close() is called

    if 't' in mode:
        return io.TextIOWrapper(process.stdout, encoding, errors, newline)
    else:
        return process.stdout


def open_regular(file, mode, encoding, errors, newline, external, parallel):
    # Simply ignore 'external' and 'parallel' args
    return io.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# Gzip
#

def open_gzip(file, mode, encoding, errors, newline, external, parallel):
    executable = None
    if external:
        if parallel:
            executable = which('pigz')
        if executable is None:
            executable = which('gzip')

    if executable is not None:
        return make_process_wrapper(
            [executable, '-c', '-d', file],
            mode, encoding=encoding, errors=errors, newline=newline)

    return gzip.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# Bzip2
#

def open_bzip2(file, mode, encoding, errors, newline, external, parallel):
    executable = None
    if external:
        if parallel:
            executable = which('pbzip2')
        if executable is None:
            executable = which('bzip2')

    if executable is not None:
        return make_process_wrapper(
            [executable, '-c', '-d', file],
            mode, encoding=encoding, errors=errors, newline=newline)

    return bz2.open(
        file, mode=mode, encoding=encoding, errors=errors, newline=newline)


#
# XZ/LZMA
#

def open_lzma(file, mode, encoding, errors, newline, external, parallel):
    executable = None
    if external:
        executable = which('xz')

    if executable is not None:
        return make_process_wrapper(
            [executable, '-c', '-d', file],
            mode, encoding=encoding, errors=errors, newline=newline)

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
