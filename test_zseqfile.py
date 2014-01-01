
import bz2
import gzip
import io
import lzma
import os

import zseqfile


def test_open(tmpdir):

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

    for fn in (regular_file, gzip_file, bzip2_file, xz_file):

        # Text mode
        fp = zseqfile.open(fn, 'rt')
        assert fp.read() == data_text
        fp.close()

        # Binary mode
        fp = zseqfile.open(fn, 'rb')
        assert fp.read() == data_binary
        fp.close()
