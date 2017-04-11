# -*- coding: utf-8 -*-
"""
test_compound3d
~~~~~~~~~~~~~~~

Test compound object with 3D record.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pubchempy import *


@pytest.fixture
def c3d():
    """Compound CID 1234, 3D."""
    return Compound.from_cid(1234, record_type='3d')


def test_properties_types(c3d):
    assert isinstance(c3d.volume_3d, float)
    assert isinstance(c3d.multipoles_3d, list)
    assert isinstance(c3d.conformer_rmsd_3d, float)
    assert isinstance(c3d.effective_rotor_count_3d, int)
    assert isinstance(c3d.pharmacophore_features_3d, list)
    assert isinstance(c3d.mmff94_partial_charges_3d, list)
    assert isinstance(c3d.mmff94_energy_3d, float)
    assert isinstance(c3d.conformer_id_3d, text_types)
    assert isinstance(c3d.shape_selfoverlap_3d, float)
    assert isinstance(c3d.feature_selfoverlap_3d, float)
    assert isinstance(c3d.shape_fingerprint_3d, list)
    assert isinstance(c3d.volume_3d, float)


def test_coordinate_type(c3d):
    assert c3d.coordinate_type == '3d'


def test_atoms(c3d):
    assert len(c3d.atoms) == 75
    assert set(a.element for a in c3d.atoms) == {'C', 'H', 'O', 'N'}
    assert set(c3d.elements) == {'C', 'H', 'O', 'N'}


def test_atoms_deprecated(c3d):
    with warnings.catch_warnings(record=True) as w:
        assert set(a['element'] for a in c3d.atoms) == {'C', 'H', 'O', 'N'}
        assert len(w) == 1
        assert w[0].category == PubChemPyDeprecationWarning
        assert str(w[0].message) == 'Dictionary style access to Atom attributes is deprecated'


def test_coordinates(c3d):
    for a in c3d.atoms:
        assert isinstance(a.x, (float, int))
        assert isinstance(a.y, (float, int))
        assert isinstance(a.z, (float, int))


def test_coordinates_deprecated(c3d):
    with warnings.catch_warnings(record=True) as w:
        assert isinstance(c3d.atoms[0]['x'], (float, int))
        assert isinstance(c3d.atoms[0]['y'], (float, int))
        assert isinstance(c3d.atoms[0]['z'], (float, int))
        assert len(w) == 3
        assert w[0].category == PubChemPyDeprecationWarning
        assert str(w[0].message) == 'Dictionary style access to Atom attributes is deprecated'
