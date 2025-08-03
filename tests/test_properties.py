"""Test properties requests."""

from pubchempy import get_properties, get_synonyms


def test_properties():
    """"""
    results = get_properties(
        ["SMILES", "InChIKey"], "tris-(1,10-phenanthroline)ruthenium", "name"
    )
    assert len(results) > 0
    for result in results:
        assert "CID" in result
        assert "SMILES" in result
        assert "InChIKey" in result


def test_underscore_properties():
    """Properties can be specified as snake_case and CamelCase."""
    results = get_properties(
        ["smiles", "molecular_weight"], "tris-(1,10-phenanthroline)ruthenium", "name"
    )
    assert len(results) > 0
    for result in results:
        assert "CID" in result
        assert "SMILES" in result
        assert "MolecularWeight" in result


def test_comma_string_properties():
    """Properties can be specified as a comma-separated string rather than a list."""
    results = get_properties(
        "smiles,InChIKey,molecular_weight",
        "tris-(1,10-phenanthroline)ruthenium",
        "name",
    )
    assert len(results) > 0
    for result in results:
        assert "CID" in result
        assert "SMILES" in result
        assert "MolecularWeight" in result
        assert "InChIKey" in result


def test_synonyms():
    results = get_synonyms("C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1", "smiles")
    assert len(results) > 0
    for result in results:
        assert "CID" in result
        assert "Synonym" in result
        assert isinstance(result["Synonym"], list)
        assert len(result["Synonym"]) > 0
