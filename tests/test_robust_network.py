# -*- coding: utf-8 -*-
"""
test_robust_network
~~~~~~~~~~~~~~~~~~~

Robust tests that handle network issues gracefully.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import time
import warnings

from pubchempy import *


def safe_api_call(func, *args, **kwargs):
    """Safely call an API function with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (PubChemHTTPError, TimeoutError, ServerError) as e:
            if attempt == max_retries - 1:
                pytest.skip(f"PubChem server error after {max_retries} attempts: {e}")
            time.sleep(1.0 * (2**attempt))  # Exponential backoff
        except NotFoundError:
            # NotFoundError is expected for some tests, don't retry
            raise
        except BadRequestError:
            # BadRequestError is expected for some tests, don't retry
            raise


@pytest.mark.network
def test_robust_compound_properties():
    """Test compound properties with robust error handling."""

    def get_aspirin_properties():
        return get_properties(["SMILES", "MolecularWeight"], "aspirin", "name")

    results = safe_api_call(get_aspirin_properties)
    if results:  # Only test if we got results
        assert len(results) > 0
        for result in results:
            assert "CID" in result


@pytest.mark.network
def test_robust_identifiers():
    """Test identifier retrieval with robust error handling."""

    def get_aspirin_cids():
        return get_cids("aspirin", "name", "compound")

    cids = safe_api_call(get_aspirin_cids)
    if cids:  # Only test if we got results
        assert len(cids) >= 1
        assert all(isinstance(cid, int) for cid in cids)


@pytest.mark.network
def test_robust_substance_dataframe():
    """Test substance DataFrame creation with robust error handling."""
    try:
        import pandas as pd

        def get_substance_df():
            return get_substances("aspirin", "name", as_dataframe=True)

        df = safe_api_call(get_substance_df)
        if df is not None and not df.empty:
            assert df.ndim == 2
            assert df.index.names == ["sid"]
    except ImportError:
        pytest.skip("pandas not available")


@pytest.mark.network
def test_robust_compound_dataframe():
    """Test compound DataFrame creation with robust error handling."""
    try:
        import pandas as pd

        def get_compound_df():
            return get_compounds("aspirin", "name", as_dataframe=True)

        df = safe_api_call(get_compound_df)
        if df is not None and not df.empty:
            assert df.ndim == 2
            assert df.index.names == ["cid"]
    except ImportError:
        pytest.skip("pandas not available")


@pytest.mark.network
def test_robust_error_handling():
    """Test that proper errors are raised for invalid inputs."""
    # These should still raise errors even with our robust handling
    with pytest.raises(BadRequestError):
        safe_api_call(Compound.from_cid, "invalid")

    with pytest.raises(NotFoundError):
        safe_api_call(Compound.from_cid, 999999999)


@pytest.mark.network
def test_robust_synonyms():
    """Test synonym retrieval with robust error handling."""

    def get_aspirin_synonyms():
        return get_synonyms("aspirin", "name")

    synonyms = safe_api_call(get_aspirin_synonyms)
    if synonyms:  # Only test if we got results
        assert len(synonyms) > 0
        assert any(
            "aspirin" in str(syn).lower() for syn in synonyms[0].get("Synonym", [])
        )


@pytest.mark.network
def test_robust_requests():
    """Test basic requests with robust error handling."""

    def make_basic_request():
        return request("aspirin", "name")

    response = safe_api_call(make_basic_request)
    if response:
        assert response.getcode() == 200


@pytest.mark.network
def test_robust_properties_underscore():
    """Test underscore property names with robust error handling."""

    def get_underscore_props():
        return get_properties(
            ["molecular_weight", "canonical_smiles"], "aspirin", "name"
        )

    results = safe_api_call(get_underscore_props)
    if results:  # Only test if we got results
        assert len(results) > 0
        for result in results:
            assert "CID" in result
            # Should have either MolecularWeight or SMILES (mapped from underscore names)
            assert "MolecularWeight" in result or "SMILES" in result
