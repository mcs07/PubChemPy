"""
test_download
~~~~~~~~~~~~~

Test downloading.

"""

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
    download('CSV', os.path.join(tmp_dir, 's.csv'), [1, 2, 3], operation='property/ConnectivitySMILES,SMILES')
    with open(os.path.join(tmp_dir, 's.csv')) as f:
        rows = list(csv.reader(f))
        assert rows[0] == ['CID', 'ConnectivitySMILES', 'SMILES']
        assert rows[1][0] == '1'
        assert rows[2][0] == '2'
        assert rows[3][0] == '3'
