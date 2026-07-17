# RCC-8 topology, evaluated numerically on definite scenes (regions, not constraint networks) -> O(1) per pair.

from __future__ import annotations

from .geometry import Aabb

CODES: tuple[str, ...] = ("DC", "EC", "PO", "TPP", "TPPi", "NTPP", "NTPPi", "EQ")

# What the lexicon's prose maps to. 'is within' is a disjunction; RCC-8 genuinely separates it from 'is inside'.
PROSE: dict[str, tuple[str, ...]] = {
    "is clear of": ("DC",),
    "touches": ("EC",),
    "rests on": ("EC",),
    "overlaps": ("PO",),
    "is inside": ("NTPP",),
    "is within": ("TPP", "NTPP"),
    "contains": ("TPPi", "NTPPi"),
    "coincides with": ("EQ",),
}


def relation(a: Aabb, b: Aabb, eps: float) -> str:
    """The single RCC-8 relation holding between two regions within tolerance eps."""
    overlaps = _axis_overlaps(a, b)
    tightest = min(overlaps)
    if tightest < -eps:
        return "DC"
    if tightest <= eps:
        return "EC"
    if _is_equal(a, b, eps):
        return "EQ"
    if _is_part(a, b, eps):
        result = "NTPP" if _is_strict_part(a, b, eps) else "TPP"
        return result
    if _is_part(b, a, eps):
        result = "NTPPi" if _is_strict_part(b, a, eps) else "TPPi"
        return result
    return "PO"


def _axis_overlaps(a: Aabb, b: Aabb) -> list[float]:
    overlaps = []
    for axis in range(3):
        upper = min(a.hi[axis], b.hi[axis])
        lower = max(a.lo[axis], b.lo[axis])
        overlaps.append(upper - lower)
    return overlaps


def _is_equal(a: Aabb, b: Aabb, eps: float) -> bool:
    for axis in range(3):
        if abs(a.lo[axis] - b.lo[axis]) > eps:
            return False
        if abs(a.hi[axis] - b.hi[axis]) > eps:
            return False
    return True


def _is_part(inner: Aabb, outer: Aabb, eps: float) -> bool:
    """inner is contained in outer, allowing flush faces."""
    for axis in range(3):
        if inner.lo[axis] < outer.lo[axis] - eps:
            return False
        if inner.hi[axis] > outer.hi[axis] + eps:
            return False
    return True


def _is_strict_part(inner: Aabb, outer: Aabb, eps: float) -> bool:
    """inner is contained in outer with clearance on every face: NTPP rather than TPP."""
    for axis in range(3):
        if inner.lo[axis] - outer.lo[axis] <= eps:
            return False
        if outer.hi[axis] - inner.hi[axis] <= eps:
            return False
    return True


def holds(a: Aabb, b: Aabb, expected: tuple[str, ...], eps: float) -> tuple[bool, str]:
    """Whether the region pair satisfies any of the expected RCC-8 codes; also returns the code found."""
    found = relation(a, b, eps)
    result = found in expected
    return (result, found)
