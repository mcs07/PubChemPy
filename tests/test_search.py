# -*- coding: utf-8 -*-
"""
test_search
~~~~~~~~~~~

Test searching.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pubchempy import *


def test_search_assays():
    assays = get_assays([1, 1000, 490])
    for assay in assays:
        assert isinstance(assay.name, text_types)


def test_substructure():
    results = get_compounds('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles', searchtype='substructure', listkey_count=3)
    assert len(results) == 3
    for result in results:
        assert all(el in [a['element'] for a in result.atoms] for el in {'C', 'N', 'H'})
        assert result.heavy_atom_count >= 14
