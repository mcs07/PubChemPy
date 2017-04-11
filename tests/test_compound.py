# -*- coding: utf-8 -*-
"""
test_compound
~~~~~~~~~~~~~

Test compound object.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re

import pytest

from pubchempy import *


@pytest.fixture(scope='module')
def c1():
    """Compound CID 241."""
    return Compound.from_cid(241)


@pytest.fixture(scope='module')
def c2():
    """Compound CID 175."""
    return Compound.from_cid(175)


def test_basic(c1):
    """Test Compound is retrieved and has a record and correct CID."""
    assert c1.cid == 241
    assert repr(c1) == 'Compound(241)'
    assert c1.record


def test_atoms(c1):
    assert len(c1.atoms) == 12
    assert set(a.element for a in c1.atoms) == {'C', 'H'}
    assert set(c1.elements) == {'C', 'H'}


def test_atoms_deprecated(c1):
    with warnings.catch_warnings(record=True) as w:
        assert set(a['element'] for a in c1.atoms) == {'C', 'H'}
        assert len(w) == 1
        assert w[0].category == PubChemPyDeprecationWarning
        assert str(w[0].message) == 'Dictionary style access to Atom attributes is deprecated'


def test_single_atom():
    """Test Compound when there is a single atom and no bonds."""
    c = Compound.from_cid(259)
    assert c.atoms == [Atom(aid=1, number=35, x=2, y=0, charge=-1)]
    assert c.bonds == []


def test_bonds(c1):
    assert len(c1.bonds) == 12
    assert set(b.order for b in c1.bonds) == {BondType.SINGLE, BondType.DOUBLE}


def test_bonds_deprecated(c1):
    with warnings.catch_warnings(record=True) as w:
        assert set(b['order'] for b in c1.bonds) == {BondType.SINGLE, BondType.DOUBLE}
        assert len(w) == 1
        assert w[0].category == PubChemPyDeprecationWarning
        assert str(w[0].message) == 'Dictionary style access to Bond attributes is deprecated'


def test_charge(c1):
    assert c1.charge == 0


def test_coordinates(c1):
    for a in c1.atoms:
        assert isinstance(a.x, (float, int))
        assert isinstance(a.y, (float, int))
        assert a.z is None


def test_coordinates_deprecated(c1):
    with warnings.catch_warnings(record=True) as w:
        assert isinstance(c1.atoms[0]['x'], (float, int))
        assert isinstance(c1.atoms[0]['y'], (float, int))
        assert 'z' not in c1.atoms[0]
        assert len(w) == 3
        assert w[0].category == PubChemPyDeprecationWarning
        assert str(w[0].message) == 'Dictionary style access to Atom attributes is deprecated'


def test_identifiers(c1):
    assert len(c1.canonical_smiles) > 10
    assert len(c1.isomeric_smiles) > 10
    assert c1.inchi.startswith('InChI=')
    assert re.match(r'^[A-Z]{14}-[A-Z]{10}-[A-Z\d]$', c1.inchikey)
    # TODO: c1.molecular_formula


def test_properties_types(c1):
    assert isinstance(c1.molecular_weight, float)
    assert isinstance(c1.iupac_name, text_types)
    assert isinstance(c1.xlogp, float)
    assert isinstance(c1.exact_mass, float)
    assert isinstance(c1.monoisotopic_mass, float)
    assert isinstance(c1.tpsa, (int, float))
    assert isinstance(c1.complexity, float)
    assert isinstance(c1.h_bond_donor_count, int)
    assert isinstance(c1.h_bond_acceptor_count, int)
    assert isinstance(c1.rotatable_bond_count, int)
    assert isinstance(c1.heavy_atom_count, int)
    assert isinstance(c1.isotope_atom_count, int)
    assert isinstance(c1.atom_stereo_count, int)
    assert isinstance(c1.defined_atom_stereo_count, int)
    assert isinstance(c1.undefined_atom_stereo_count, int)
    assert isinstance(c1.bond_stereo_count, int)
    assert isinstance(c1.defined_bond_stereo_count, int)
    assert isinstance(c1.undefined_bond_stereo_count, int)
    assert isinstance(c1.covalent_unit_count, int)
    assert isinstance(c1.fingerprint, text_types)


def test_coordinate_type(c1):
    assert c1.coordinate_type == '2d'


def test_compound_equality():
    assert Compound.from_cid(241) == Compound.from_cid(241)
    assert get_compounds('Benzene', 'name')[0], get_compounds('c1ccccc1' == 'smiles')[0]


def test_synonyms(c1):
    assert len(c1.synonyms) > 5
    assert len(c1.synonyms) > 5


def test_related_records(c1):
    assert len(c1.sids) > 20
    assert len(c1.aids) > 20


def test_compound_dict(c1):
    assert isinstance(c1.to_dict(), dict)
    assert c1.to_dict()
    assert 'atoms' in c1.to_dict()
    assert 'bonds' in c1.to_dict()
    assert 'element' in c1.to_dict()['atoms'][0]


def test_charged_compound(c2):
    assert len(c2.atoms) == 7
    assert c2.atoms[0].charge == -1


def test_charged_compound_deprecated(c2):
    with warnings.catch_warnings(record=True) as w:
        assert c2.atoms[0]['charge'] == -1
        assert len(w) == 1
        assert w[0].category == PubChemPyDeprecationWarning
        assert str(w[0].message) == 'Dictionary style access to Atom attributes is deprecated'


def test_fingerprint(c1):
    # CACTVS fingerprint is 881 bits
    assert len(c1.cactvs_fingerprint) == 881
    # Raw fingerprint has 4 byte prefix, 7 bit suffix, and is hex encoded (/4) = 230
    assert len(c1.fingerprint) == (881 + (4 * 8) + 7) / 4
