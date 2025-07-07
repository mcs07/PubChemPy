# -*- coding: utf-8 -*-
"""
conftest.py
~~~~~~~~~~~

Pytest configuration and shared fixtures for pubchempy tests.

"""

import pytest
import time
import warnings
import threading
from http.client import RemoteDisconnected
from urllib.error import URLError
from pubchempy import *
import pubchempy

# Global rate limiting
_last_request_time = 0
_request_lock = threading.Lock()
_original_request = None


def rate_limited_request(min_delay=0.5):
    """Ensure minimum delay between API requests to avoid overwhelming PubChem servers."""
    global _last_request_time
    with _request_lock:
        current_time = time.time()
        elapsed = current_time - _last_request_time
        if elapsed < min_delay:
            time.sleep(min_delay - elapsed)
        _last_request_time = time.time()


def patched_request(*args, **kwargs):
    """Patched version of pubchempy.request that includes rate limiting."""
    rate_limited_request(0.3)  # 300ms minimum delay between API calls
    return _original_request(*args, **kwargs)


def retry_on_server_error(func, max_retries=3, delay=1.0):
    """Retry a function call on server errors (503, 504, 500) and network errors."""
    for attempt in range(max_retries):
        try:
            # Add rate limiting before each request
            rate_limited_request()
            return func()
        except (
            PubChemHTTPError,
            TimeoutError,
            ServerError,
            RemoteDisconnected,
            URLError,
            ConnectionError,
        ) as e:
            if attempt == max_retries - 1:
                # On final attempt, skip the test instead of failing
                pytest.skip(f"Network/server error after {max_retries} attempts: {e}")
            time.sleep(delay * (2**attempt))  # Exponential backoff
        except Exception as e:
            # For other exceptions, don't retry
            raise


@pytest.fixture(scope="session")
def robust_compound():
    """Get a simple compound with retry logic."""

    def get_compound():
        return Compound.from_cid(2244)  # Aspirin - very reliable

    return retry_on_server_error(get_compound)


@pytest.fixture(scope="session")
def robust_3d_compound():
    """Get a 3D compound with retry logic."""

    def get_3d_compound():
        return Compound.from_cid(2244, record_type="3d")  # Aspirin 3D

    return retry_on_server_error(get_3d_compound)


@pytest.fixture(scope="session")
def robust_substance():
    """Get a substance with retry logic."""

    def get_substance():
        return Substance.from_sid(46507415)  # Reliable substance

    return retry_on_server_error(get_substance)


@pytest.fixture(scope="session")
def robust_assay():
    """Get an assay with retry logic."""

    def get_assay():
        return Assay.from_aid(1)  # AID 1 is very stable

    return retry_on_server_error(get_assay)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (may skip in CI)")
    config.addinivalue_line(
        "markers", "network: marks tests as requiring network access"
    )

    # Monkey patch the request function to add rate limiting
    global _original_request
    _original_request = pubchempy.request
    pubchempy.request = patched_request


def pytest_unconfigure(config):
    """Restore original request function after tests."""
    global _original_request
    if _original_request:
        pubchempy.request = _original_request


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle network-dependent tests."""
    for item in items:
        # Mark all tests as network tests since they hit PubChem API
        item.add_marker(pytest.mark.network)

        # Add slow marker to tests that might take longer
        if any(
            keyword in item.name.lower() for keyword in ["3d", "download", "search"]
        ):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def handle_server_errors():
    """Automatically handle server errors in all tests."""
    # This fixture runs before each test
    # Add a small delay to prevent overwhelming servers
    rate_limited_request(0.2)  # 200ms minimum between tests
    yield
