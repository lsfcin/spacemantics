# Numeric predicates: DIST (point-to-region), and the orientation family (faces / aligned / parallel / perpendicular).

from __future__ import annotations

import math

from . import vecmath as vm
from .geometry import point_to_region_distance
from .scene import Scene
from .units import Quantity

OPS: dict[str, str] = {"<": "<", "<=": "<=", ">": ">", ">=": ">=", "==": "=="}


class PredicateError(Exception):
    """The predicate cannot be evaluated on this scene as declared."""


def distance(scene: Scene, figure: str, ground: str, t: float = 0.0) -> float:
    """Schematized: the figure collapses to a point, the ground keeps its region."""
    centre = scene.centre_of(figure, t)
    region = scene.region_of(ground, t)
    result = point_to_region_distance(centre, region)
    return result


def distance_holds(
    scene: Scene, figure: str, ground: str, op: str, quantity: Quantity, t: float = 0.0
) -> tuple[bool, str]:
    """DIST vs a unit-tagged threshold. An ordinal quantity raises UnitTypeError here — by design (C2)."""
    if op not in OPS:
        raise PredicateError(f"unknown comparison '{op}'")
    threshold = quantity.to_metres(scene.units)
    measured = distance(scene, figure, ground, t)
    eps = scene.tolerance.length
    verdict = compare(measured, op, threshold, eps)
    detail = f"distance={measured:.4f}m {op} {threshold:.4f}m (eps={eps}m)"
    return (verdict, detail)


def compare(measured: float, op: str, threshold: float, eps: float) -> bool:
    if op == "<":
        result = measured < threshold + eps
    elif op == "<=":
        result = measured <= threshold + eps
    elif op == ">":
        result = measured > threshold - eps
    elif op == ">=":
        result = measured >= threshold - eps
    else:
        result = abs(measured - threshold) <= eps
    return result


def faces(scene: Scene, subject: str, target: str, t: float = 0.0) -> tuple[bool, str]:
    """angle(front axis of A, A->B) ~ 0. Requires A to have a front — otherwise it is not a claim at all."""
    if not scene.has_front(subject):
        entity = scene.entity(subject)
        raise PredicateError(f"'{entity.type}' has no front, so it cannot face anything")
    entity = scene.entity(subject)
    _, orientation = entity.pose_at(t)
    _, forward, _ = vm.basis_of(orientation)
    subject_centre = scene.centre_of(subject, t)
    target_centre = scene.centre_of(target, t)
    towards = vm.sub(target_centre, subject_centre)
    angle = vm.angle_between(forward, towards)
    eps = scene.tolerance.angle
    verdict = angle <= eps
    detail = f"angle={math.degrees(angle):.2f}deg (eps={math.degrees(eps):.2f}deg)"
    return (verdict, detail)


def axis_angle_holds(scene: Scene, a: str, b: str, expected_deg: float, t: float = 0.0) -> tuple[bool, str]:
    """parallel (0deg) / perpendicular (90deg) between the two objects' forward axes.

    Axes are undirected: an antiparallel pair is parallel, so the angle folds into [0, 90].
    """
    entity_a = scene.entity(a)
    entity_b = scene.entity(b)
    _, orientation_a = entity_a.pose_at(t)
    _, orientation_b = entity_b.pose_at(t)
    _, forward_a, _ = vm.basis_of(orientation_a)
    _, forward_b, _ = vm.basis_of(orientation_b)
    angle = vm.angle_between(forward_a, forward_b)
    folded = min(angle, math.pi - angle)
    target = math.radians(expected_deg)
    eps = scene.tolerance.angle
    verdict = abs(folded - target) <= eps
    detail = f"axis-angle={math.degrees(folded):.2f}deg, expected {expected_deg:.0f}deg (eps={math.degrees(eps):.2f}deg)"
    return (verdict, detail)


def aligned(scene: Scene, a: str, b: str, axis: str = "x", t: float = 0.0) -> tuple[bool, str]:
    """Edge/axis collinearity within the length tolerance: the two centres agree on the named axis."""
    index = {"x": 0, "y": 1, "z": 2}.get(axis)
    if index is None:
        raise PredicateError(f"unknown alignment axis '{axis}'")
    centre_a = scene.centre_of(a, t)
    centre_b = scene.centre_of(b, t)
    delta = abs(centre_a[index] - centre_b[index])
    eps = scene.tolerance.length
    verdict = delta <= eps
    detail = f"delta_{axis}={delta:.4f}m (eps={eps}m)"
    return (verdict, detail)
