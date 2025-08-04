"""Test depositor sources."""

from pubchempy import get_all_sources


def test_substance_sources():
    """Retrieve a list of all Substance sources."""
    substance_sources = get_all_sources()
    assert len(substance_sources) > 20
    assert isinstance(substance_sources, list)
    assert "SureChEMBL" in substance_sources
    assert "DiscoveryGate" in substance_sources
    assert "ZINC" in substance_sources


def test_assay_sources():
    """Retrieve a list of all Assay sources."""
    assay_sources = get_all_sources("assay")
    assert len(assay_sources) > 20
    assert isinstance(assay_sources, list)
    assert "ChEMBL" in assay_sources
    assert "DTP/NCI" in assay_sources
