"""Pytest configuration for PubChemPy tests."""

# import time

# import pytest


# @pytest.fixture(autouse=True)
# def rate_limit_tests():
#     """Limit the rate of requests to PubChem.
#
#     This fixture ensures that there is a delay between tests to avoid hitting
#     PubChem's rate limits, which can cause PubChemHTTPError: 'PUGREST.ServerBusy' to be
#     raised. A delay of 1 second is automatically applied between every test.
#     """
#     yield
#     time.sleep(1)
