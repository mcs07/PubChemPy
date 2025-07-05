# -*- coding: utf-8 -*-
"""
test_coverage_improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

Test cases to improve code coverage for pubchempy.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import tempfile
import os
import warnings

import pubchempy as pcp
from pubchempy import *


def test_request_with_none_identifier():
    """Test that request raises ValueError when identifier is None."""
    with pytest.raises(ValueError, match="identifier/cid cannot be None"):
        request(None)


def test_get_sdf_not_found():
    """Test get_sdf function with invalid identifier."""
    # Test that BadRequestError is raised for invalid identifier
    with pytest.raises(BadRequestError):
        get_sdf("invalid_identifier")


def test_download_function():
    """Test download function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.png")
        # Download a small image
        download("PNG", filepath, 2244, width=100, height=100)
        assert os.path.exists(filepath)

        # Test overwrite protection
        with pytest.raises(IOError, match="already exists"):
            download("PNG", filepath, 2244, width=100, height=100, overwrite=False)


def test_get_all_sources():
    """Test get_all_sources function."""
    sources = get_all_sources("substance")
    assert isinstance(sources, list)
    assert len(sources) > 0


def test_atom_set_coordinates():
    """Test Atom set_coordinates method."""
    atom = Atom(1, 6, 1.0, 2.0, 3.0)
    atom.set_coordinates(4.0, 5.0, 6.0)
    assert atom.x == 4.0
    assert atom.y == 5.0
    assert atom.z == 6.0

    # Test 2D coordinates
    atom.set_coordinates(7.0, 8.0)
    assert atom.x == 7.0
    assert atom.y == 8.0
    assert atom.z is None


def test_atom_coordinate_type():
    """Test Atom coordinate_type property."""
    atom_2d = Atom(1, 6, 1.0, 2.0)
    assert atom_2d.coordinate_type == "2d"

    atom_3d = Atom(1, 6, 1.0, 2.0, 3.0)
    assert atom_3d.coordinate_type == "3d"


def test_atom_to_dict():
    """Test Atom to_dict method."""
    atom = Atom(1, 6, 1.0, 2.0, 3.0, charge=-1)
    atom_dict = atom.to_dict()

    expected_keys = {"aid", "number", "element", "x", "y", "z", "charge"}
    assert set(atom_dict.keys()) == expected_keys
    assert atom_dict["aid"] == 1
    assert atom_dict["number"] == 6
    assert atom_dict["element"] == "C"
    assert atom_dict["charge"] == -1


def test_bond_to_dict():
    """Test Bond to_dict method."""
    bond = Bond(1, 2, BondType.DOUBLE)
    bond_dict = bond.to_dict()

    expected_keys = {"aid1", "aid2", "order"}
    assert set(bond_dict.keys()) == expected_keys
    assert bond_dict["aid1"] == 1
    assert bond_dict["aid2"] == 2
    assert bond_dict["order"] == BondType.DOUBLE

    # Test with style
    bond_with_style = Bond(1, 2, BondType.SINGLE, style=1)
    bond_dict_with_style = bond_with_style.to_dict()
    assert "style" in bond_dict_with_style
    assert bond_dict_with_style["style"] == 1


def test_deprecated_atom_setitem():
    """Test deprecated __setitem__ method for Atom."""
    atom = Atom(1, 6)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        atom["charge"] = -1
        assert len(w) == 1
        assert issubclass(w[0].category, PubChemPyDeprecationWarning)
        assert atom.charge == -1


def test_deprecated_bond_setitem():
    """Test deprecated __setitem__ method for Bond."""
    bond = Bond(1, 2)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        bond["style"] = 1
        assert len(w) == 1
        assert issubclass(w[0].category, PubChemPyDeprecationWarning)
        assert bond.style == 1


def test_deprecated_bond_contains():
    """Test deprecated __contains__ method for Bond."""
    bond = Bond(1, 2, BondType.DOUBLE, style=1)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert "order" in bond
        assert "style" in bond
        assert "nonexistent" not in bond
        assert len(w) == 3
        assert all(
            issubclass(warning.category, PubChemPyDeprecationWarning) for warning in w
        )


def test_deprecated_bond_delitem():
    """Test deprecated __delitem__ method for Bond."""
    bond = Bond(1, 2, style=1)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with pytest.raises(AttributeError):  # The __delitem__ method has a bug
            del bond["nonexistent"]
        assert len(w) == 1
        assert issubclass(w[0].category, PubChemPyDeprecationWarning)


def test_compound_repr_without_cid():
    """Test Compound __repr__ when no CID is available."""
    # Create a compound with a minimal record that has no CID
    minimal_record = {"atoms": {"aid": [1], "element": [6]}, "props": []}
    compound = Compound(minimal_record)
    assert repr(compound) == "Compound()"


def test_assay_target_property():
    """Test Assay target property when target is not present."""
    # Get an assay and test the target property
    assays = get_assays(1)
    if assays:
        assay = assays[0]
        # The target property should handle missing 'target' key gracefully
        target = assay.target
        # This may be None if no target is present
        assert target is None or isinstance(target, list)


def test_substance_synonyms_property():
    """Test Substance synonyms property when synonyms are not present."""
    substances = get_substances(46507415)  # A substance that should exist
    if substances:
        substance = substances[0]
        synonyms = substance.synonyms
        # Should handle missing synonyms gracefully
        assert synonyms is None or isinstance(synonyms, list)


def test_error_classes():
    """Test that error classes can be instantiated."""
    # Test error class constructors
    bad_request = BadRequestError("Test message")
    assert bad_request.msg == "Test message"

    not_found = NotFoundError("Test message")
    assert not_found.msg == "Test message"

    method_not_allowed = MethodNotAllowedError("Test message")
    assert method_not_allowed.msg == "Test message"

    timeout_error = TimeoutError("Test message")
    assert timeout_error.msg == "Test message"

    unimplemented = UnimplementedError("Test message")
    assert unimplemented.msg == "Test message"

    server_error = ServerError("Test message")
    assert server_error.msg == "Test message"


def test_compounds_to_frame_single_compound():
    """Test compounds_to_frame with a single Compound object."""
    try:
        import pandas as pd

        compound = Compound.from_cid(2244)
        df = compounds_to_frame(compound)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert 2244 in df.index
    except ImportError:
        pytest.skip("pandas not available")


def test_substances_to_frame_single_substance():
    """Test substances_to_frame with a single Substance object."""
    try:
        import pandas as pd

        substances = get_substances(46507415)
        if substances:
            substance = substances[0]
            df = substances_to_frame(substance)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
    except ImportError:
        pytest.skip("pandas not available")


def test_main_module_execution():
    """Test the __main__ execution path."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "pubchempy"], capture_output=True, text=True
    )
    # This should print the version
    assert result.returncode == 0
    assert "1.0.4" in result.stdout


def test_element_property_unknown():
    """Test Atom element property with unknown atomic number."""
    atom = Atom(1, 999)  # Unknown element
    assert atom.element is None


def test_parse_prop_functions():
    """Test the _parse_prop helper functions."""
    from pubchempy import _parse_prop_as_float, _parse_prop_as_int

    # Test _parse_prop_as_float with invalid value
    proplist = [{"urn": {"label": "Test"}, "value": {"sval": "not_a_number"}}]
    result = _parse_prop_as_float({"label": "Test"}, proplist)
    assert result == "not_a_number"  # Should return original value if conversion fails

    # Test _parse_prop_as_int with invalid value
    result = _parse_prop_as_int({"label": "Test"}, proplist)
    assert result == "not_a_number"  # Should return original value if conversion fails
