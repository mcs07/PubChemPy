# -*- coding: utf-8 -*-
"""
test_download
~~~~~~~~~~~~~

Test downloading.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import csv
import shutil
import tempfile

import pytest

from pubchempy import *


@pytest.fixture(scope='module')
def tmp_dir():
    dir = tempfile.mkdtemp()
    yield dir
    shutil.rmtree(dir)


def test_image_download(tmp_dir):
    download('PNG', os.path.join(tmp_dir, 'aspirin.png'), 'Aspirin', 'name')
    with pytest.raises(IOError):
        download('PNG', os.path.join(tmp_dir, 'aspirin.png'), 'Aspirin', 'name')
    download('PNG', os.path.join(tmp_dir, 'aspirin.png'), 'Aspirin', 'name', overwrite=True)


def test_csv_download(tmp_dir):
    download('CSV', os.path.join(tmp_dir, 's.csv'), [1, 2, 3], operation='property/CanonicalSMILES,IsomericSMILES')
    with open(os.path.join(tmp_dir, 's.csv')) as f:
        rows = list(csv.reader(f))
        assert rows[0] == ['CID', 'CanonicalSMILES', 'IsomericSMILES']
        assert rows[1][0] == '1'
        assert rows[2][0] == '2'
        assert rows[3][0] == '3'
