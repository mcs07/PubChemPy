# -*- coding: utf-8 -*-
"""
Unit tests for pubchempy.py

Python interface for the PubChem PUG REST service.
https://github.com/mcs07/PubChemPy
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import csv
import logging
import os
import re
import shutil
import tempfile
import unittest

import pandas as pd

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
        """"""
        results = get_properties(['IsomericSMILES', 'InChIKey'], 'tris-(1,10-phenanthroline)ruthenium', 'name')
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('CID', result)
            self.assertIn('IsomericSMILES', result)
            self.assertIn('InChIKey', result)

    def test_underscore_properties(self):
        """Properties can also be specified as underscore-separated words, rather than CamelCase."""
        results = get_properties(['isomeric_smiles', 'molecular_weight'], 'tris-(1,10-phenanthroline)ruthenium', 'name')
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('CID', result)
            self.assertIn('IsomericSMILES', result)
            self.assertIn('MolecularWeight', result)

    def test_comma_string_properties(self):
        """Properties can also be specified as a comma-separated string, rather than a list."""
        results = get_properties('isomeric_smiles,InChIKey,molecular_weight', 'tris-(1,10-phenanthroline)ruthenium', 'name')
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('CID', result)
            self.assertIn('IsomericSMILES', result)
            self.assertIn('MolecularWeight', result)
            self.assertIn('InChIKey', result)

    def test_synonyms(self):
        results = get_synonyms('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles')
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('CID', result)
            self.assertIn('Synonym', result)
            self.assertTrue(isinstance(result['Synonym'], list))
            self.assertGreater(len(result['Synonym']), 0)


class TestIdentifiers(unittest.TestCase):

    def test_identifiers_from_name(self):
        """Use a name input to retrieve lists of identifiers."""
        # Get CID for each compound linked to substances with name Aspirin
        self.assertGreaterEqual(len(get_cids('Aspirin', 'name', 'substance')), 10)
        # Get CID for each compound with name Aspirin
        self.assertEqual(len(get_cids('Aspirin', 'name', 'compound')), 1)
        # Get SID for substances linked to compound with name Aspirin
        self.assertGreaterEqual(len(get_sids('Aspirin', 'name', 'substance')), 10)
        # Get AID for each assay linked to substances with name Aspirin
        self.assertGreaterEqual(len(get_aids('Aspirin', 'name', 'substance')), 10)
        # Get AID for each assay linked to compound with name Aspirin
        self.assertEqual(len(get_aids('Aspirin', 'name', 'compound')), 1)

    def test_no_identifiers(self):
        """Test retrieving no identifier results."""
        self.assertEqual(get_cids('asfgaerghaeirughae', 'name', 'substance'), [])
        self.assertEqual(get_cids('asfgaerghaeirughae', 'name', 'compound'), [])
        self.assertEqual(get_sids(999999999, 'cid', 'compound'), [])
        self.assertEqual(get_aids(150194, 'cid', 'compound'), [])


class TestCompound(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c1 = Compound.from_cid(241)
        cls.c2 = Compound.from_cid(175)

    def test_basic(self):
        """Test Compound is retrieved and has a record and correct CID."""
        self.assertEqual(self.c1.cid, 241)
        self.assertEqual(repr(self.c1), 'Compound(241)')
        self.assertTrue(self.c1.record)

    def test_atoms(self):
        self.assertEqual(len(self.c1.atoms), 12)
        self.assertEqual(set(a.element for a in self.c1.atoms), {'c', 'h'})
        self.assertEqual(set(self.c1.elements), {'c', 'h'})

    def test_atoms_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(set(a['element'] for a in self.c1.atoms), {'c', 'h'})
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PubChemPyDeprecationWarning)
            self.assertEqual(str(w[0].message), 'Dictionary style access to Atom attributes is deprecated')

    def test_single_atom(self):
        """Test Compound when there is a single atom and no bonds."""
        c = Compound.from_cid(259)
        self.assertEqual(c.atoms, [Atom(aid=1, element='br', x=2, y=0, charge=-1)])
        self.assertEqual(c.bonds, [])

    def test_bonds(self):
        self.assertEqual(len(self.c1.bonds), 12)
        self.assertEqual(set(b.order for b in self.c1.bonds), {'single', 'double'})

    def test_bonds_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(set(b['order'] for b in self.c1.bonds), {'single', 'double'})
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PubChemPyDeprecationWarning)
            self.assertEqual(str(w[0].message), 'Dictionary style access to Bond attributes is deprecated')

    def test_charge(self):
        self.assertEqual(self.c1.charge, 0)

    def test_coordinates(self):
        for a in self.c1.atoms:
            self.assertIsInstance(a.x, (float, int))
            self.assertIsInstance(a.y, (float, int))
            self.assertEqual(a.z, None)

    def test_coordinates_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertTrue(isinstance(self.c1.atoms[0]['x'], (float, int)))
            self.assertTrue(isinstance(self.c1.atoms[0]['y'], (float, int)))
            self.assertNotIn('z', self.c1.atoms[0])
            self.assertEqual(len(w), 3)
            self.assertEqual(w[0].category, PubChemPyDeprecationWarning)
            self.assertEqual(str(w[0].message), 'Dictionary style access to Atom attributes is deprecated')

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
        self.assertTrue(isinstance(self.c1.monoisotopic_mass, float))
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

    def test_synonyms(self):
        self.assertGreater(len(self.c1.synonyms), 5)
        self.assertGreater(len(self.c1.synonyms), 5)

    def test_related_records(self):
        self.assertGreater(len(self.c1.sids), 20)
        self.assertGreater(len(self.c1.aids), 20)

    def test_compound_dict(self):
        self.assertTrue(isinstance(self.c1.to_dict(), dict))
        self.assertTrue(self.c1.to_dict())
        self.assertIn('atoms', self.c1.to_dict())
        self.assertIn('bonds', self.c1.to_dict())
        self.assertIn('element', self.c1.to_dict()['atoms'][0])

    def test_charged_compound(self):
        self.assertEqual(len(self.c2.atoms), 7)
        self.assertEqual(self.c2.atoms[0].charge, -1)

    def test_charged_compound_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(self.c2.atoms[0]['charge'], -1)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PubChemPyDeprecationWarning)
            self.assertEqual(str(w[0].message), 'Dictionary style access to Atom attributes is deprecated')


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

    def test_atoms(self):
        self.assertEqual(len(self.c1.atoms), 75)
        self.assertEqual(set(a.element for a in self.c1.atoms), {'c', 'h', 'o', 'n'})
        self.assertEqual(set(self.c1.elements), {'c', 'h', 'o', 'n'})

    def test_atoms_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(set(a['element'] for a in self.c1.atoms), {'c', 'h', 'o', 'n'})
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PubChemPyDeprecationWarning)
            self.assertEqual(str(w[0].message), 'Dictionary style access to Atom attributes is deprecated')

    def test_coordinates(self):
        for a in self.c1.atoms:
            self.assertIsInstance(a.x, (float, int))
            self.assertIsInstance(a.y, (float, int))
            self.assertIsInstance(a.z, (float, int))

    def test_coordinates_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            self.assertTrue(isinstance(self.c1.atoms[0]['x'], (float, int)))
            self.assertTrue(isinstance(self.c1.atoms[0]['y'], (float, int)))
            self.assertTrue(isinstance(self.c1.atoms[0]['z'], (float, int)))
            self.assertEqual(len(w), 3)
            self.assertEqual(w[0].category, PubChemPyDeprecationWarning)
            self.assertEqual(str(w[0].message), 'Dictionary style access to Atom attributes is deprecated')


class TestSubstance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.s1 = Substance.from_sid(24864499)

    def test_basic(self):
        """Test Substance is retrieved and has a record and correct SID."""
        self.assertEqual(self.s1.sid, 24864499)
        self.assertEqual(repr(self.s1), 'Substance(24864499)')
        self.assertTrue(self.s1.record)

    def test_substance_equality(self):
        self.assertEqual(Substance.from_sid(24864499), Substance.from_sid(24864499))
        self.assertEqual(get_substances('Coumarin 343', 'name')[0], get_substances(24864499)[0])

    def test_synonyms(self):
        self.assertGreater(len(self.s1.synonyms), 1)

    def test_source(self):
        self.assertEqual(self.s1.source_name, 'Sigma-Aldrich')
        self.assertEqual(self.s1.source_id, '393029_ALDRICH')

    def test_deposited_compound(self):
        """Check that a Compound object can be constructed from the embedded deposited compound record."""
        self.assertTrue(self.s1.deposited_compound.record)

    def test_deposited_compound2(self):
        """Check that a Compound object can be constructed from the embedded deposited compound record."""
        s2 = Substance.from_sid(223766453)
        self.assertTrue(s2.deposited_compound.record)

    def test_standardized_compound(self):
        """Check the CID is correct and that the Compound can be retrieved."""
        self.assertEqual(self.s1.standardized_cid, 108770)
        self.assertEqual(self.s1.standardized_compound.cid, 108770)

    def test_related_records(self):
        self.assertEqual(len(self.s1.cids), 1)
        self.assertEqual(len(self.s1.aids), 0)

    def test_substance_dict(self):
        self.assertTrue(isinstance(self.s1.to_dict(), dict))
        self.assertTrue(self.s1.to_dict())


class TestAssay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.a1 = Assay.from_aid(490)

    def test_basic(self):
        self.assertEqual(self.a1.aid, 490)
        self.assertEqual(repr(self.a1), 'Assay(490)')
        self.assertTrue(self.a1.record)

    def test_meta(self):
        self.assertTrue(isinstance(self.a1.name, text_types))
        self.assertEqual(self.a1.project_category, 'literature-extracted')
        self.assertTrue(isinstance(self.a1.description, list))
        self.assertTrue(isinstance(self.a1.comments, list))

    def test_assay_equality(self):
        first = Assay.from_aid(490)
        second = Assay.from_aid(1000)
        self.assertEqual(first, first)
        self.assertEqual(second, second)
        self.assertNotEqual(first, second)

    def test_assay_dict(self):
        self.assertTrue(isinstance(self.a1.to_dict(), dict))
        self.assertTrue(self.a1.to_dict())


class TestSearch(unittest.TestCase):

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


class TestDownload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()

    def test_image_download(self):
        download('PNG', os.path.join(self.dir, 'aspirin.png'), 'Aspirin', 'name')
        with self.assertRaises(IOError):
            download('PNG', os.path.join(self.dir, 'aspirin.png'), 'Aspirin', 'name')
        download('PNG', os.path.join(self.dir, 'aspirin.png'), 'Aspirin', 'name', overwrite=True)

    def test_csv_download(self):
        download('CSV', os.path.join(self.dir, 's.csv'), [1, 2, 3], operation='property/CanonicalSMILES,IsomericSMILES')
        with open(os.path.join(self.dir, 's.csv')) as f:
            rows = list(csv.reader(f))
            self.assertEqual(rows[0], ['CID', 'CanonicalSMILES', 'IsomericSMILES'])
            self.assertEqual(rows[1][0], '1')
            self.assertEqual(rows[2][0], '2')
            self.assertEqual(rows[3][0], '3')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)


class TestErrors(unittest.TestCase):

    def test_invalid_identifier(self):
        """BadRequestError should be raised if identifier is not a positive integer."""
        with self.assertRaises(BadRequestError):
            Compound.from_cid('aergaerhg')
        with self.assertRaises(BadRequestError):
            get_compounds('srthrthsr')
        with self.assertRaises(BadRequestError):
            get_substances('grgrqjksa')

    def test_notfound_identifier(self):
        """NotFoundError should be raised if identifier is a positive integer but record doesn't exist."""
        with self.assertRaises(NotFoundError):
            Compound.from_cid(999999999)
        with self.assertRaises(NotFoundError):
            Substance.from_sid(999999999)

    def test_notfound_search(self):
        """No error should be raised if a search returns no results."""
        get_compounds(999999999)
        get_substances(999999999)


class TestSources(unittest.TestCase):

    def test_substance_sources(self):
        """Retrieve a list of all Substance sources."""
        substance_sources = get_all_sources()
        self.assertGreater(len(substance_sources), 20)
        self.assertTrue(isinstance(substance_sources, list))
        self.assertIn('SureChEMBL', substance_sources)
        self.assertIn('DiscoveryGate', substance_sources)
        self.assertIn('ZINC', substance_sources)

    def test_assay_sources(self):
        """Retrieve a list of all Assay sources."""
        assay_sources = get_all_sources('assay')
        self.assertGreater(len(assay_sources), 20)
        self.assertTrue(isinstance(assay_sources, list))
        self.assertIn('ChEMBL', assay_sources)
        self.assertIn('DTP/NCI', assay_sources)


class TestPandas(unittest.TestCase):

    def test_compounds_dataframe(self):
        """"""
        df = get_compounds('C20H41Br', 'formula', as_dataframe=True)
        self.assertEqual(df.ndim, 2)
        self.assertEqual(df.index.names, ['cid'])
        self.assertGreater(len(df.index), 5)
        columns = df.columns.values.tolist()
        self.assertIn('atom_stereo_count', columns)
        self.assertIn('atoms', columns)
        self.assertIn('canonical_smiles', columns)
        self.assertIn('exact_mass', columns)

    def test_substances_dataframe(self):
        df = get_substances([1, 2, 3, 4], as_dataframe=True)
        self.assertEqual(df.ndim, 2)
        self.assertEqual(df.index.names, ['sid'])
        self.assertEqual(len(df.index), 4)
        self.assertEqual(df.columns.values.tolist(), ['source_id', 'source_name', 'standardized_cid', 'synonyms'])

    def test_properties_dataframe(self):
        df = get_properties(['isomeric_smiles', 'xlogp', 'inchikey'], '1,2,3,4', 'cid', as_dataframe=True)
        self.assertEqual(df.ndim, 2)
        self.assertEqual(df.index.names, ['CID'])
        self.assertEqual(len(df.index), 4)
        self.assertEqual(df.columns.values.tolist(), ['InChIKey', 'IsomericSMILES', 'XLogP'])

    def test_compound_series(self):
        s = Compound.from_cid(241).to_series()
        self.assertTrue(isinstance(s, pd.Series))

    def test_substance_series(self):
        s = Substance.from_sid(1234).to_series()
        self.assertTrue(isinstance(s, pd.Series))

    def test_compound_to_frame(self):
        s = compounds_to_frame(Compound.from_cid(241))
        self.assertTrue(isinstance(s, pd.DataFrame))

    def test_substance_to_frame(self):
        s = substances_to_frame(Substance.from_sid(1234))
        self.assertTrue(isinstance(s, pd.DataFrame))


INCHIKEY_RE = re.compile(r'^[A-Z]{14}-[A-Z]{10}-[A-Z\d]$')
INCHI_RE = re.compile(r'^(InChI=)?1S?/(p\+1|\d*[a-ik-z][a-ik-z\d\.]*(/c[\d\-*(),;]+)?(/h[\d\-*h(),;]+)?)'
                      r'(/[bmpqst][\d\-\.+*,;?]*|/i[hdt\d\-+*,;]*(/h[hdt\d]+)?|'
                      r'/r[a-ik-z\d]+(/c[\d\-*(),;]+)?(/h[\d\-*h(),;]+)?|/f[a-ik-z\d]*(/h[\d\-*h(),;]+)?)*$', re.I)
SMILES_RE = re.compile(r'^([BCNOPSFIbcnosp*]|Cl|Br|\[\d*([A-Za-z]s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\])'
                       r'([BCNOPSFIbcnosp*]|Cl|Br|\[\d*([A-Za-z]s|se|as|\*)(@+([THALSPBO]\d+)?)?(H\d?)?([\-+]+\d*)?(:\d+)?\]|'
                       r'[\-=#$:\\/\(\)%%\.+\d])*$')


if __name__ == '__main__':
    unittest.main()

