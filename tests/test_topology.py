# RCC-8 must produce all eight codes on definite regions, and 'is inside' must genuinely differ from 'is within'.

from __future__ import annotations

import pytest

from checker.geometry import Aabb
from checker.rcc8 import relation

EPS = 0.005


def box(lo, hi) -> Aabb:
    return Aabb(tuple(lo), tuple(hi))


UNIT = box((0, 0, 0), (1, 1, 1))


@pytest.mark.parametrize(
    "other,expected",
    [
        (box((2, 2, 2), (3, 3, 3)), "DC"),
        (box((1, 0, 0), (2, 1, 1)), "EC"),
        (box((0.5, 0, 0), (1.5, 1, 1)), "PO"),
        (box((0.25, 0.25, 0.25), (0.75, 0.75, 0.75)), "NTPPi"),
        (box((0, 0, 0), (0.5, 0.5, 0.5)), "TPPi"),
        (box((0, 0, 0), (1, 1, 1)), "EQ"),
    ],
)
def test_relation_codes(other, expected):
    found = relation(UNIT, other, EPS)
    assert found == expected


def test_inverse_codes():
    inner = box((0.25, 0.25, 0.25), (0.75, 0.75, 0.75))
    assert relation(inner, UNIT, EPS) == "NTPP"
    flush = box((0, 0, 0), (0.5, 0.5, 0.5))
    assert relation(flush, UNIT, EPS) == "TPP"


def test_inside_is_not_within():
    """The one distinction users must learn: a tile flush against a wall is TPP, not NTPP."""
    flush = box((0, 0, 0), (0.5, 0.5, 0.5))
    clear = box((0.25, 0.25, 0.25), (0.75, 0.75, 0.75))
    assert relation(flush, UNIT, EPS) == "TPP"  # 'is within' -> yes; 'is inside' -> no
    assert relation(clear, UNIT, EPS) == "NTPP"  # both


def test_tolerance_decides_contact_versus_gap():
    near = box((1.002, 0, 0), (2, 1, 1))
    assert relation(UNIT, near, EPS) == "EC"  # inside tolerance: touching
    far = box((1.02, 0, 0), (2, 1, 1))
    assert relation(UNIT, far, EPS) == "DC"  # outside tolerance: a gap
