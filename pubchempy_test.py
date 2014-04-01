# -*- coding: utf-8 -*-
"""
Unit tests for pubchempy.py

Python interface for the PubChem PUG REST service.
https://github.com/mcs07/PubChemPy
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import logging
import re
import unittest

from pubchempy import *


logging.basicConfig(level=logging.DEBUG)


class TestRequest(unittest.TestCase):

    def test_requests(self):
        """Test a variety of basic raw requests and ensure they don't return an error code."""
        self.assertEqual(request('c1ccccc1', 'smiles').getcode(), 200)
        self.assertEqual(request('DTP/NCI', 'sourceid', 'substance', '747285', 'SDF').getcode(), 200)
        self.assertEqual(request('coumarin', 'name', output='PNG', image_size='50x50').getcode(), 200)

    def test_content_type(self):
        """Test content type header matches desired output format."""
        self.assertEqual(request(241, output='JSON').headers['Content-Type'], 'application/json')
        self.assertEqual(request(241, output='XML').headers['Content-Type'], 'application/xml')
        self.assertEqual(request(241, output='SDF').headers['Content-Type'], 'chemical/x-mdl-sdfile')
        self.assertEqual(request(241, output='ASNT').headers['Content-Type'], 'text/plain')
        self.assertEqual(request(241, output='PNG').headers['Content-Type'], 'image/png')

    def test_listkey_requests(self):
        """Test asynchronous listkey requests."""
        r1 = get_json('CC', 'smiles', operation='cids', searchtype='superstructure')
        self.assertTrue('IdentifierList' in r1 and 'CID' in r1['IdentifierList'])
        r2 = get_json('C10H21N', 'formula', listkey_count=3)
        self.assertTrue('PC_Compounds' in r2 and len(r2['PC_Compounds']) == 3)


class TestProperties(unittest.TestCase):

    def test_properties(self):
        print(get_properties('IsomericSMILES', 'tris-(1,10-phenanthroline)ruthenium', 'name'))

    def test_synonyms(self):
        print(get_synonyms('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles'))

    def test_csaids(self):
        print(get_cids('Aspirin', 'name', 'substance'))
        print(get_cids('Aspirin', 'name', 'compound'))
        print(get_sids('Aspirin', 'name', 'substance'))
        print(get_aids('Aspirin', 'name', 'substance'))
        print(get_aids('Aspirin', 'name', 'compound'))


class TestCompound(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c1 = Compound.from_cid(241)

    def test_basic(self):
        """Test Compound is retrieved and has a record and correct CID."""
        self.assertEqual(self.c1.cid, 241)
        self.assertTrue(self.c1.record)

    def test_atoms(self):
        self.assertEqual(len(self.c1.atoms), 12)
        self.assertEqual(set(a['element'] for a in self.c1.atoms), {'c', 'h'})

    def test_bonds(self):
        self.assertEqual(len(self.c1.bonds), 12)
        self.assertEqual(set(b['order'] for b in self.c1.bonds), {'single', 'double'})

    def test_charge(self):
        self.assertEqual(self.c1.charge, 0)

    def test_identifiers(self):
        self.assertTrue(SMILES_RE.match(self.c1.canonical_smiles))
        self.assertTrue(SMILES_RE.match(self.c1.isomeric_smiles))
        self.assertTrue(INCHI_RE.match(self.c1.inchi))
        self.assertTrue(INCHIKEY_RE.match(self.c1.inchikey))
        # TODO: self.c1.molecular_formula

    def test_properties_types(self):
        self.assertTrue(isinstance(self.c1.molecular_weight, float))
        self.assertTrue(isinstance(self.c1.iupac_name, text_types))
        self.assertTrue(isinstance(self.c1.xlogp, float))
        self.assertTrue(isinstance(self.c1.exact_mass, float))
        self.assertTrue(isinstance(self.c1.tpsa, (int, float)))
        self.assertTrue(isinstance(self.c1.complexity, float))
        self.assertTrue(isinstance(self.c1.h_bond_donor_count, int))
        self.assertTrue(isinstance(self.c1.h_bond_acceptor_count, int))
        self.assertTrue(isinstance(self.c1.rotatable_bond_count, int))
        self.assertTrue(isinstance(self.c1.heavy_atom_count, int))
        self.assertTrue(isinstance(self.c1.isotope_atom_count, int))
        self.assertTrue(isinstance(self.c1.atom_stereo_count, int))
        self.assertTrue(isinstance(self.c1.defined_atom_stereo_count, int))
        self.assertTrue(isinstance(self.c1.undefined_atom_stereo_count, int))
        self.assertTrue(isinstance(self.c1.bond_stereo_count, int))
        self.assertTrue(isinstance(self.c1.defined_bond_stereo_count, int))
        self.assertTrue(isinstance(self.c1.undefined_bond_stereo_count, int))
        self.assertTrue(isinstance(self.c1.covalent_unit_count, int))
        self.assertTrue(isinstance(self.c1.fingerprint, text_types))

    def test_coordinate_type(self):
        self.assertEqual(self.c1.coordinate_type, '2d')

    def test_compound_equality(self):
        self.assertEqual(Compound.from_cid(241), Compound.from_cid(241))
        self.assertEqual(get_compounds('Benzene', 'name')[0], get_compounds('c1ccccc1', 'smiles')[0])

    def test_compound_hash(self):
        self.assertEqual(hash(Compound.from_cid(241)), hash(Compound.from_cid(241)))
        self.assertEqual(hash(get_compounds('Benzene', 'name')[0]), hash(get_compounds('c1ccccc1', 'smiles')[0]))


class TestCompound3d(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c1 = Compound.from_cid(1234, record_type='3d')

    def test_properties_types(self):
        self.assertTrue(isinstance(self.c1.volume_3d, float))
        self.assertTrue(isinstance(self.c1.multipoles_3d, list))
        self.assertTrue(isinstance(self.c1.conformer_rmsd_3d, float))
        self.assertTrue(isinstance(self.c1.effective_rotor_count_3d, int))
        self.assertTrue(isinstance(self.c1.pharmacophore_features_3d, list))
        self.assertTrue(isinstance(self.c1.mmff94_partial_charges_3d, list))
        self.assertTrue(isinstance(self.c1.mmff94_energy_3d, float))
        self.assertTrue(isinstance(self.c1.conformer_id_3d, text_types))
        self.assertTrue(isinstance(self.c1.shape_selfoverlap_3d, float))
        self.assertTrue(isinstance(self.c1.feature_selfoverlap_3d, float))
        self.assertTrue(isinstance(self.c1.shape_fingerprint_3d, list))
        self.assertTrue(isinstance(self.c1.volume_3d, float))

    def test_coordinate_type(self):
        self.assertEqual(self.c1.coordinate_type, '3d')


class TestAssay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a1 = Assay.from_aid(490)

    def test_aid(self):
        self.assertEqual(self.a1.aid, 490)

    def test_meta(self):
        self.assertTrue(isinstance(self.a1.name, text_types))
        self.assertEqual(self.a1.project_category, 'literature-extracted')
        self.assertTrue(isinstance(self.a1.description, list))
        self.assertTrue(isinstance(self.a1.comments, list))


class TestSearch(unittest.TestCase):

    maxDiff = None

    def test_search_assays(self):
        assays = get_assays([1, 1000, 490])
        for assay in assays:
            self.assertTrue(isinstance(assay.name, text_types))

    def test_substructure(self):
        results = get_compounds('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles', searchtype='substructure', listkey_count=3)
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(all(el in [a['element'] for a in result.atoms] for el in {'c', 'n', 'h'}))
            self.assertTrue(result.heavy_atom_count >= 14)



INCHIKEY_RE = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z\d]$')
INCHI_RE = re.compile(r'^(InChI=)?1S?/(p\+1|\d*[a-ik-z][a-ik-z\d\.]*(/c[\d\-*(),;]+)?(/h[\d\-*h(),;]+)?)'
                      r'(/[bmpqst][\d\-\.+*,;?]*|/i[hdt\d\-+*,;]*(/h[hdt\d]+)?|'
                      r'/r[a-ik-z\d]+(/c[\d\-*(),;]+)?(/h[\d\-*h(),;]+)?|/f[a-ik-z\d]*(/h[\d\-*h(),;]+)?)*$', re.I)
SMILES_RE = re.compile(r'^([BCNOPSFIbcnosp*]|Cl|Br|\[\d*([A-Za-z]s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\])'
                       r'([BCNOPSFIbcnosp*]|Cl|Br|\[\d*([A-Za-z]s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\]|'
                       r'[\-=#$:\\/\(\)%%\.+\d])*$')


if __name__ == '__main__':
    unittest.main()

