"""Test downloading."""

import csv

import pytest

from pubchempy import download


def test_image_download(tmp_path):
    download("PNG", tmp_path / "aspirin.png", "Aspirin", "name")
    with pytest.raises(OSError):
        download("PNG", tmp_path / "aspirin.png", "Aspirin", "name")
    download("PNG", tmp_path / "aspirin.png", "Aspirin", "name", overwrite=True)


def test_csv_download(tmp_path):
    props = "property/ConnectivitySMILES,SMILES"
    download("CSV", tmp_path / "s.csv", [1, 2, 3], operation=props)
    with open(tmp_path / "s.csv") as f:
        rows = list(csv.reader(f))
        assert rows[0] == ["CID", "ConnectivitySMILES", "SMILES"]
        assert rows[1][0] == "1"
        assert rows[2][0] == "2"
        assert rows[3][0] == "3"
