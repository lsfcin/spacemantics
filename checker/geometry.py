# Regions: the only geometric primitive the checker owns. Shape + pose -> an axis-aligned box, plus its support interval along any axis.

from __future__ import annotations

from dataclasses import dataclass

from . import vecmath as vm
from .vecmath import Quat, Vec3

Interval = tuple[float, float]


@dataclass(frozen=True)
class Aabb:
    """Axis-aligned bounding region in the canonical frame."""

    lo: Vec3
    hi: Vec3

    def centre(self) -> Vec3:
        summed = vm.add(self.lo, self.hi)
        result = vm.scaled(summed, 0.5)
        return result

    def half_extent(self) -> Vec3:
        span = vm.sub(self.hi, self.lo)
        result = vm.scaled(span, 0.5)
        return result


def box_region(position: Vec3, orientation: Quat, extent: Vec3) -> Aabb:
    """A box under an arbitrary rotation is bounded by the AABB of its rotated half-extent.

    Exact when the rotation is axis-aligned; conservative otherwise. The kernel is honest about this:
    see checker/CONTEXT.md 'Known approximations'.
    """
    half = vm.scaled(extent, 0.5)
    right, forward, up = vm.basis_of(orientation)
    spread = _abs_span(right, forward, up, half)
    lo = vm.sub(position, spread)
    hi = vm.add(position, spread)
    return Aabb(lo, hi)


def _abs_span(right: Vec3, forward: Vec3, up: Vec3, half: Vec3) -> Vec3:
    span = []
    for axis in range(3):
        contribution = abs(right[axis]) * half[0] + abs(forward[axis]) * half[1] + abs(up[axis]) * half[2]
        span.append(contribution)
    result = (span[0], span[1], span[2])
    return result


def sphere_region(position: Vec3, radius: float) -> Aabb:
    offset = (radius, radius, radius)
    lo = vm.sub(position, offset)
    hi = vm.add(position, offset)
    return Aabb(lo, hi)


def point_region(position: Vec3) -> Aabb:
    return Aabb(position, position)


def interval_along(region: Aabb, axis: Vec3) -> Interval:
    """Support interval of the region projected onto a unit axis (Rectangle Algebra's per-axis interval)."""
    unit = vm.normalize(axis)
    centre = region.centre()
    half = region.half_extent()
    middle = vm.dot(centre, unit)
    reach = abs(unit[0]) * half[0] + abs(unit[1]) * half[1] + abs(unit[2]) * half[2]
    return (middle - reach, middle + reach)


def point_to_region_distance(point: Vec3, region: Aabb) -> float:
    """Schematization: the figure collapses to a point, the ground keeps its region (foundations §3).

    Zero when the point lies inside the ground.
    """
    gaps = []
    for axis in range(3):
        below = region.lo[axis] - point[axis]
        above = point[axis] - region.hi[axis]
        gap = max(0.0, below, above)
        gaps.append(gap)
    outside = (gaps[0], gaps[1], gaps[2])
    result = vm.length(outside)
    return result
