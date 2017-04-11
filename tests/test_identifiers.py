# -*- coding: utf-8 -*-
"""
test_indentifiers
~~~~~~~~~~~~~~~~~

Test identifiers requests.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pubchempy import *


def test_identifiers_from_name():
    """Use a name input to retrieve lists of identifiers."""
    # Get CID for each compound linked to substances with name Aspirin
    assert len(get_cids('Aspirin', 'name', 'substance')) >= 10
    # Get CID for each compound with name Aspirin
    assert len(get_cids('Aspirin', 'name', 'compound')) >= 1
    # Get SID for substances linked to compound with name Aspirin
    assert len(get_sids('Aspirin', 'name', 'substance')) >= 10
    # Get AID for each assay linked to substances with name Aspirin
    assert len(get_aids('Aspirin', 'name', 'substance')) >= 10
    # Get AID for each assay linked to compound with name Aspirin
    assert len(get_aids('Aspirin', 'name', 'compound')) >= 1


def test_no_identifiers():
    """Test retrieving no identifier results."""
    assert get_cids('asfgaerghaeirughae', 'name', 'substance') == []
    assert get_cids('asfgaerghaeirughae', 'name', 'compound') == []
    assert get_sids(999999999, 'cid', 'compound') == []
    assert get_aids(150194, 'cid', 'compound') == []
