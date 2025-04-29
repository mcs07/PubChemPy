#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""general instructions for pytest tests"""

import time
import pytest


@pytest.fixture(autouse=True)
def pause_between_tests():
    """limit the rate the PubChem database is queried

    Running pytest e.g., with GitHub's runner of Ubuntu 24.04
    can cause checks run within a set of test scripts to fail
    while else -- if individually launched -- they pass.  An
    occasional report by pytest in lines of

    ```
    pubchempy.PubChemHTTPError: 'PUGREST.ServerBusy'
    ```

    appears indicative PubChem set a throttle with a threshold
    of calls set lower, than the tests would normally run, too.
    This fixture addresses this problem."""
    yield
    time.sleep(2)
