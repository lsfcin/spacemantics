# DIR: projective direction under the three anchors (world / locale / group), decided by Rectangle Algebra on the anchor axis.

from __future__ import annotations

from . import allen
from . import vecmath as vm
from .geometry import interval_along
from .scene import Scene
from .vecmath import UP, Vec3

WORLD_TERMS: dict[str, Vec3] = {
    "above": (0.0, 0.0, 1.0),
    "below": (0.0, 0.0, -1.0),
    "north": (0.0, 1.0, 0.0),
    "south": (0.0, -1.0, 0.0),
    "east": (1.0, 0.0, 0.0),
    "west": (-1.0, 0.0, 0.0),
}

PROJECTIVE_TERMS: frozenset[str] = frozenset({"left", "right", "front", "behind"})


class AnchorError(Exception):
    """The arity gate: a projective term with no frame to read it in. Refused, never guessed (SPEC §1.2)."""


def axis_for(term: str, anchor: dict, scene: Scene, ground: str, t: float) -> Vec3:
    """The unit vector the term names, in the frame the anchor selects."""
    if term in WORLD_TERMS:
        return WORLD_TERMS[term]
    if term not in PROJECTIVE_TERMS:
        raise AnchorError(f"unknown direction term '{term}'")
    kind = anchor.get("kind", "world")
    if kind == "world":
        raise AnchorError(
            f"'{term}' is not world-anchored: it needs the ground's own front (locale) "
            f"or a viewpoint ('seen from V')"
        )
    if kind == "locale":
        result = _locale_axis(term, scene, ground, t)
    elif kind == "group":
        result = _group_axis(term, anchor, scene, ground, t)
    else:
        raise AnchorError(f"unknown anchor kind '{kind}'")
    return result


def _locale_axis(term: str, scene: Scene, ground: str, t: float) -> Vec3:
    if not scene.has_front(ground):
        entity = scene.entity(ground)
        raise AnchorError(
            f"'{entity.type}' has no intrinsic front — '{term} of the {ground}' is unreadable; "
            f'add "seen from <viewpoint>"'
        )
    entity = scene.entity(ground)
    _, orientation = entity.pose_at(t)
    right, forward, _ = vm.basis_of(orientation)
    axes = {
        "front": forward,
        "behind": vm.scaled(forward, -1.0),
        "right": right,
        "left": vm.scaled(right, -1.0),
    }
    return axes[term]


def _group_axis(term: str, anchor: dict, scene: Scene, ground: str, t: float) -> Vec3:
    name = anchor.get("viewpoint")
    if name is None:
        raise AnchorError("a group anchor needs a bound viewpoint (arity gate)")
    viewpoint = scene.viewpoint(name)
    ground_centre = scene.centre_of(ground, t)
    view_dir = vm.normalize(vm.sub(ground_centre, viewpoint.position))
    right = vm.normalize(vm.cross(view_dir, UP))
    transform = anchor.get("transform", "reflected")
    if transform != "reflected":
        raise AnchorError(f"group transform '{transform}' is declared but not implemented in the thin kernel")
    # 'reflected' = the English convention: the viewer's left, and 'in front of' = nearer the viewer.
    axes = {
        "left": vm.scaled(right, -1.0),
        "right": right,
        "front": vm.scaled(view_dir, -1.0),
        "behind": view_dir,
    }
    return axes[term]


def holds(scene: Scene, figure: str, ground: str, term: str, anchor: dict, t: float = 0.0) -> tuple[bool, str]:
    """A is <term> of B iff A's support interval lies wholly beyond B's along the term's axis (Allen after|met_by)."""
    axis = axis_for(term, anchor, scene, ground, t)
    figure_region = scene.region_of(figure, t)
    ground_region = scene.region_of(ground, t)
    figure_interval = interval_along(figure_region, axis)
    ground_interval = interval_along(ground_region, axis)
    eps = scene.tolerance.length
    found = allen.relation(figure_interval, ground_interval, eps)
    verdict = found in allen.BEYOND
    margin = figure_interval[0] - ground_interval[1]
    detail = f"axis-relation={found}, margin={margin:+.4f}m"
    return (verdict, detail)
