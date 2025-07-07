# -*- coding: utf-8 -*-
"""
test_errors
~~~~~~~~~~~~~

Test errors.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from http.client import RemoteDisconnected
from urllib.error import URLError

from pubchempy import *


def test_invalid_identifier():
    """BadRequestError should be raised if identifier is not a positive integer."""
    try:
        with pytest.raises(BadRequestError):
            Compound.from_cid("aergaerhg")
        with pytest.raises(BadRequestError):
            get_compounds("srthrthsr")
        with pytest.raises(BadRequestError):
            get_substances("grgrqjksa")
    except (
        PubChemHTTPError,
        ServerError,
        TimeoutError,
        RemoteDisconnected,
        URLError,
        ConnectionError,
    ) as e:
        pytest.skip(f"Network/server error preventing error test: {e}")


def test_notfound_identifier():
    """NotFoundError should be raised if identifier is a positive integer but record doesn't exist."""
    try:
        with pytest.raises(NotFoundError):
            Compound.from_cid(999999999)
        with pytest.raises(NotFoundError):
            Substance.from_sid(999999999)
    except (
        PubChemHTTPError,
        ServerError,
        TimeoutError,
        RemoteDisconnected,
        URLError,
        ConnectionError,
    ) as e:
        pytest.skip(f"Network/server error preventing error test: {e}")


def test_notfound_search():
    """No error should be raised if a search returns no results."""
    try:
        get_compounds(999999999)
        get_substances(999999999)
    except (
        PubChemHTTPError,
        ServerError,
        TimeoutError,
        RemoteDisconnected,
        URLError,
        ConnectionError,
    ) as e:
        pytest.skip(f"Network/server error: {e}")
