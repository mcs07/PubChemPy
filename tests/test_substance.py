# -*- coding: utf-8 -*-
"""
test_substance
~~~~~~~~~~~~~~

Test substance object.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pubchempy import *


@pytest.fixture(scope='module')
def s1():
    """Substance SID 24864499."""
    return Substance.from_sid(24864499)


def test_basic(s1):
    """Test Substance is retrieved and has a record and correct SID."""
    assert s1.sid == 24864499
    assert repr(s1) == 'Substance(24864499)'
    assert s1.record


def test_substance_equality():
    assert Substance.from_sid(24864499) == Substance.from_sid(24864499)
    assert get_substances('Coumarin 343, Dye Content 97 %', 'name')[0] == get_substances(24864499)[0]


def test_synonyms(s1):
    assert len(s1.synonyms) == 1


def test_source(s1):
    assert s1.source_name == 'Sigma-Aldrich'
    assert s1.source_id == '393029_ALDRICH'


def test_deposited_compound(s1):
    """Check that a Compound object can be constructed from the embedded deposited compound record."""
    assert s1.deposited_compound.record


def test_deposited_compound2():
    """Check that a Compound object can be constructed from the embedded deposited compound record."""
    s2 = Substance.from_sid(223766453)
    assert s2.deposited_compound.record


def test_standardized_compound(s1):
    """Check the CID is correct and that the Compound can be retrieved."""
    assert s1.standardized_cid == 108770
    assert s1.standardized_compound.cid == 108770


def test_related_records(s1):
    assert len(s1.cids) == 1
    assert len(s1.aids) == 0


def test_substance_dict(s1):
    assert isinstance(s1.to_dict(), dict)
    assert s1.to_dict()
