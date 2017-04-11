# -*- coding: utf-8 -*-
"""
test_pandas
~~~~~~~~~~~

Test optional pandas functionality.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pubchempy import *


log = logging.getLogger(__name__)


# Import pandas as pd, skipping tests in this module if pandas is not installed
pd = pytest.importorskip('pandas')


def test_compounds_dataframe():
    """"""
    df = get_compounds('C20H41Br', 'formula', as_dataframe=True)
    assert df.ndim == 2
    assert df.index.names == ['cid']
    assert len(df.index) > 5
    columns = df.columns.values.tolist()
    assert 'atom_stereo_count' in columns
    assert 'atoms' in columns
    assert 'canonical_smiles' in columns
    assert 'exact_mass' in columns


def test_substances_dataframe():
    df = get_substances([1, 2, 3, 4], as_dataframe=True)
    assert df.ndim == 2
    assert df.index.names == ['sid']
    assert len(df.index) == 4
    assert df.columns.values.tolist() == ['source_id', 'source_name', 'standardized_cid', 'synonyms']


def test_properties_dataframe():
    df = get_properties(['isomeric_smiles', 'xlogp', 'inchikey'], '1,2,3,4', 'cid', as_dataframe=True)
    assert df.ndim == 2
    assert df.index.names == ['CID']
    assert len(df.index) == 4
    assert df.columns.values.tolist() == ['InChIKey', 'IsomericSMILES', 'XLogP']


def test_compound_series():
    s = Compound.from_cid(241).to_series()
    assert isinstance(s, pd.Series)


def test_substance_series():
    s = Substance.from_sid(1234).to_series()
    assert isinstance(s, pd.Series)


def test_compound_to_frame():
    s = compounds_to_frame(Compound.from_cid(241))
    assert isinstance(s, pd.DataFrame)


def test_substance_to_frame():
    s = substances_to_frame(Substance.from_sid(1234))
    assert isinstance(s, pd.DataFrame)
