
import bz2
import functools
import gzip
import io
import itertools
import lzma
import os

import pytest

import zseqfile
import zseqfile.zseqfile as _zseqfile


#
# Test internal helpers
#

def test_which():
    assert _zseqfile.which('/bin/cat') == '/bin/cat'
    assert _zseqfile.which('cat') == '/bin/cat'

    assert _zseqfile.which('does-not-exist') is None
    assert _zseqfile.which('/does/not/exist') is None


@pytest.fixture
def real_gzipped_file(tmpdir):
    filename = os.path.join(str(tmpdir), "test.gz")
    with gzip.open(filename, mode='wb') as fp:
        fp.write(b"line 1\n")
        fp.write(b"line 2\n")
        fp.write(b"line 3\xe2\x80\xa6\n")  # UTF-8 encoded ellipsis
    return filename


def test_process_reader(real_gzipped_file):

    open_file = functools.partial(
        _zseqfile.ProcessIOReader,
        ['gzip', '-c', '-d'],
        real_gzipped_file)

    # Binary reading

    with open_file(mode='rb') as fp:
        assert fp.read() == b"line 1\nline 2\nline 3\xe2\x80\xa6\n"

    with open_file(mode='rb') as fp:
        assert fp.readline() == b"line 1\n"
        assert fp.read() == b"line 2\nline 3\xe2\x80\xa6\n"

    with open_file(mode='rb') as fp:
        assert fp.read(3) == b"lin"
        assert fp.read(5) == b"e 1\nl"
        assert fp.read() == b"ine 2\nline 3\xe2\x80\xa6\n"

    with open_file(mode='rb') as fp:
        expected = [b"line 1\n", b"line 2\n", b"line 3\xe2\x80\xa6\n"]
        assert list(iter(fp)) == expected

    with open_file(mode='rb') as fp:
        expected = [b"line 1\n", b"line 2\n", b"line 3\xe2\x80\xa6\n"]
        assert fp.readlines() == expected

    # Text reading

    with open_file(mode='rt') as fp:
        assert fp.read() == "line 1\nline 2\nline 3…\n"

    with open_file(mode='rt') as fp:
        assert fp.readline() == "line 1\n"
        assert fp.read() == "line 2\nline 3…\n"

    with open_file(mode='rt') as fp:
        assert fp.read(3) == "lin"
        assert fp.read(5) == "e 1\nl"
        assert fp.read() == "ine 2\nline 3…\n"

    with open_file(mode='rt') as fp:
        assert list(iter(fp)) == ["line 1\n", "line 2\n", "line 3…\n"]

    with open_file(mode='rt') as fp:
        assert fp.readlines() == ["line 1\n", "line 2\n", "line 3…\n"]


def test_process_reader_closing(real_gzipped_file):
    # File-like objects opened outside the reader should be left open
    with io.open(real_gzipped_file, mode='rb') as fp:
        reader = _zseqfile.ProcessIOReader(['gzip', '-c', '-d'], fp, mode='rb')
        reader.close()
        assert not fp.closed
        reader.close()  # calling .close() twice must succeed (as a no-op)


#
# Test public API
#


def test_valid_mode():
    with pytest.raises(ValueError):
        zseqfile.open('', mode='x')


def test_reading(tmpdir):

    tmpdir = str(tmpdir)

    line_1 = "¡!\n"
    line_2 = "line 2\n"
    data_text = line_1 + line_2
    data_binary = data_text.encode('UTF-8')

    regular_file = os.path.join(tmpdir, 'out')
    with io.open(regular_file, 'wt') as fp:
        fp.write(data_text)

    gzip_file = os.path.join(tmpdir, 'out.gz')
    with gzip.open(gzip_file, 'wt') as fp:
        fp.write(data_text)

    bzip2_file = os.path.join(tmpdir, 'out.bz2')
    with bz2.open(bzip2_file, 'wt') as fp:
        fp.write(data_text)

    xz_file = os.path.join(tmpdir, 'out.xz')
    with lzma.open(xz_file, 'wt') as fp:
        fp.write(data_text)

    for fn, external, parallel in itertools.product(
            (regular_file, gzip_file, bzip2_file, xz_file),
            (True, False),
            (True, False)):

        # Text mode
        fp = zseqfile.open(fn, 'rt', external=external, parallel=parallel)
        it = iter(fp)
        assert next(it) == line_1
        assert next(it) == line_2
        with pytest.raises(StopIteration):
            next(it)
        fp.close()

        # Binary mode
        fp = zseqfile.open(fn, 'rb', external=external, parallel=parallel)
        assert fp.read() == data_binary
        fp.close()
