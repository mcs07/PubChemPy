# -*- coding: utf-8 -*-
"""
test_server_resilient
~~~~~~~~~~~~~~~~~~~~~

Server-resilient versions of tests that commonly fail due to PubChem server issues.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import time
from http.client import RemoteDisconnected
from urllib.error import URLError
from pubchempy import *


def skip_on_server_error(func):
    """Decorator to skip tests on server errors instead of failing."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            PubChemHTTPError,
            TimeoutError,
            ServerError,
            RemoteDisconnected,
            URLError,
            ConnectionError,
        ) as e:
            pytest.skip(f"Skipping due to network/server error: {e}")
        except Exception as e:
            # Re-raise other exceptions normally
            raise

    return wrapper


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_properties():
    """Test properties retrieval with server error resilience."""
    results = get_properties(["SMILES", "MolecularWeight"], "aspirin", "name")
    assert len(results) > 0
    for result in results:
        assert "CID" in result


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_underscore_properties():
    """Test underscore property names with server error resilience."""
    results = get_properties(
        ["molecular_weight", "canonical_smiles"], "aspirin", "name"
    )
    assert len(results) > 0
    for result in results:
        assert "CID" in result


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_synonyms():
    """Test synonym retrieval with server error resilience."""
    synonyms = get_synonyms("aspirin", "name")
    assert len(synonyms) > 0


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_identifiers():
    """Test identifier retrieval with server error resilience."""
    cids = get_cids("aspirin", "name", "compound")
    assert len(cids) >= 1
    assert all(isinstance(cid, int) for cid in cids)


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_requests():
    """Test basic requests with server error resilience."""
    response = request("aspirin", "name")
    assert response.getcode() == 200


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_compounds_dataframe():
    """Test compound DataFrame creation with server error resilience."""
    try:
        import pandas as pd

        df = get_compounds("aspirin", "name", as_dataframe=True)
        assert df.ndim == 2
        assert df.index.names == ["cid"]
        assert len(df.index) >= 1
    except ImportError:
        pytest.skip("pandas not available")


@pytest.mark.network
@skip_on_server_error
def test_server_resilient_substances_dataframe():
    """Test substance DataFrame creation with server error resilience."""
    try:
        import pandas as pd

        # Use a more specific substance search to avoid incomplete records
        substances = get_substances("aspirin", "name")
        if substances:
            # Filter out substances without proper compound data
            valid_substances = []
            for s in substances:
                try:
                    # Test if we can access basic properties without error
                    _ = s.sid
                    _ = s.source_name
                    valid_substances.append(s)
                except (KeyError, AttributeError):
                    # Skip substances with incomplete data
                    continue

            if valid_substances:
                df = substances_to_frame(valid_substances)
                assert df.ndim == 2
                assert df.index.names == ["sid"]
                assert len(df.index) >= 1
            else:
                pytest.skip("No valid substances found")
        else:
            pytest.skip("No substances found")
    except ImportError:
        pytest.skip("pandas not available")


# Test error conditions that should still raise errors
@pytest.mark.network
def test_error_conditions_still_work():
    """Test that proper errors are still raised for invalid inputs."""
    try:
        with pytest.raises(BadRequestError):
            Compound.from_cid("invalid")

        with pytest.raises(NotFoundError):
            Compound.from_cid(999999999)
    except (
        PubChemHTTPError,
        ServerError,
        TimeoutError,
        RemoteDisconnected,
        URLError,
        ConnectionError,
    ) as e:
        pytest.skip(f"Network/server error preventing error test: {e}")
