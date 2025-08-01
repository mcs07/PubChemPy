"""Test assay object."""

import pytest

from pubchempy import Assay, ProjectCategory


@pytest.fixture(scope="module")
def a1():
    """Assay AID 1973374."""
    return Assay.from_aid(1973374)


def test_basic(a1):
    assert a1.aid == 1973374
    assert repr(a1) == "Assay(1973374)"
    assert a1.record


def test_meta(a1):
    assert isinstance(a1.name, str)
    assert a1.project_category == ProjectCategory.LITERATURE_EXTRACTED
    assert isinstance(a1.description, list)
    assert isinstance(a1.comments, list)


def test_assay_equality():
    first = Assay.from_aid(1973374)
    second = Assay.from_aid(273821)
    assert first == first
    assert second == second
    assert first != second


def test_assay_dict(a1):
    assert isinstance(a1.to_dict(), dict)
    assert a1.to_dict()
