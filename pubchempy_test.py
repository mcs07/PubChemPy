# -*- coding: utf-8 -*-
"""
Unit tests for pubchempy.py

Python interface for the PubChem PUG REST service.
https://github.com/mcs07/PubChemPy
"""


import unittest

from pubchempy import *

class TestPubChemPy(unittest.TestCase):
    """ These tests don't check whether the output is correct. They just check that no exception is raised. """

    def setUp(self):
        """ Define some example inputs """
        self.alaninesmiles = 'N[C@@H](C)C(=O)O'
        self.morphineinchi = [{'value': 'InChI=1/C17H19NO3/c1-18-7-6-17-10-3-5-13(20)16(17)21-15-12(19)4-2-9(14(15)17)8-11(10)18/h2-5,10-11,13,16,19-20H,6-8H2,1H3/t10-,11+,13?,16-,17-/m0/s1', 'notation': 'Morphine', 'resolver': 'cir_name'}]
        self.tntsmiles1 = '[N+](=O)([O-])C1=C(C(=CC(=C1)[N+](=O)[O-])[N+](=O)[O-])C'
        self.tntsmiles2 = 'C1=C(C=C(C(=C1[N+]([O-])=O)C)[N+]([O-])=O)[N+]([O-])=O'
        self.phenanthrolinesmiles = 'C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1'
        self.molform = 'C10H21N'

    def test_requests(self):
        """ Test basic raw requests """
        request('coumarin', 'name', record_type='3d')
        request('coumarin', 'name', output='PNG', image_size='50x50')

    def test_listkeys(self):
        """ Test asynchronous listkey requests """
        r = get(self.phenanthrolinesmiles, 'smiles', operation='cids', searchtype='substructure')
        r = get(self.molform, 'formula', listkey_count=3)

    def test_synonyms(self):
        get_synonyms(self.phenanthrolinesmiles, 'smiles')


if __name__ == '__main__':
    unittest.main()

