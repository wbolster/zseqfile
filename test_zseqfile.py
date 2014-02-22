
import bz2
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


#
# Test public API
#


def test_valid_mode():
    with pytest.raises(ValueError):
        zseqfile.open('', mode='x')


def test_reading(tmpdir):

    tmpdir = str(tmpdir)

    data_text = "¡!"
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
        assert fp.read() == data_text
        fp.close()

        # Binary mode
        fp = zseqfile.open(fn, 'rb', external=external, parallel=parallel)
        assert fp.read() == data_binary
        fp.close()
