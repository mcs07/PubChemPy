# -*- coding: utf-8 -*-
"""
test_sources
~~~~~~~~~~~~

Test sources.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from http.client import RemoteDisconnected
from urllib.error import URLError

from pubchempy import *


def test_substance_sources():
    """Retrieve a list of all Substance sources."""
    try:
        substance_sources = get_all_sources("substance")
        assert len(substance_sources) > 100
        assert isinstance(substance_sources, list)
        assert "ChemSpider" in substance_sources
        assert "EPA DSSTox" in substance_sources
    except (
        PubChemHTTPError,
        ServerError,
        TimeoutError,
        RemoteDisconnected,
        URLError,
        ConnectionError,
    ) as e:
        pytest.skip(f"Network/server error: {e}")


def test_assay_sources():
    """Retrieve a list of all Assay sources."""
    try:
        assay_sources = get_all_sources("assay")
        assert len(assay_sources) > 20
        assert isinstance(assay_sources, list)
        assert "ChEMBL" in assay_sources
        assert "DTP/NCI" in assay_sources
    except (
        PubChemHTTPError,
        ServerError,
        TimeoutError,
        RemoteDisconnected,
        URLError,
        ConnectionError,
    ) as e:
        pytest.skip(f"Network/server error: {e}")
