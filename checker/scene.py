# The scene IR the checker actually consumes: entities with pose (possibly keyframed), viewpoints, declarations, claims.

from __future__ import annotations

from dataclasses import dataclass, field

from . import vecmath as vm
from .geometry import Aabb, box_region, point_region, sphere_region
from .types import Ontology, base_ontology
from .units import UnitContext
from .vecmath import IDENTITY, Quat, Vec3


class SceneError(Exception):
    """A reference that does not resolve, or a declaration the kernel requires and did not get."""


@dataclass(frozen=True)
class Keyframe:
    t: float
    position: Vec3
    orientation: Quat


@dataclass
class Entity:
    name: str
    type: str
    shape: dict
    position: Vec3 = (0.0, 0.0, 0.0)
    orientation: Quat = IDENTITY
    keyframes: tuple[Keyframe, ...] = ()
    free: frozenset[str] = frozenset()

    def pose_at(self, t: float) -> tuple[Vec3, Quat]:
        if not self.keyframes:
            return (self.position, self.orientation)
        result = _interpolate(self.keyframes, t)
        return result


@dataclass(frozen=True)
class Viewpoint:
    name: str
    position: Vec3
    look_at: str  # an entity name; the group anchor is only bound once this resolves


@dataclass(frozen=True)
class Tolerance:
    """Mandatory. Without it, 'aligned' is not a verifiable claim (SPEC §0)."""

    length: float  # metres
    angle: float  # radians
    time: float = 1e-3  # seconds


@dataclass
class Scene:
    profile: str
    timebase: str
    tolerance: Tolerance
    units: UnitContext = field(default_factory=UnitContext)
    ontology: Ontology = field(default_factory=base_ontology)
    entities: dict[str, Entity] = field(default_factory=dict)
    viewpoints: dict[str, Viewpoint] = field(default_factory=dict)
    events: dict[str, tuple[float, float]] = field(default_factory=dict)
    claims: tuple[dict, ...] = ()

    def entity(self, name: str) -> Entity:
        found = self.entities.get(name)
        if found is None:
            raise SceneError(f"no entity named '{name}'")
        return found

    def viewpoint(self, name: str) -> Viewpoint:
        found = self.viewpoints.get(name)
        if found is None:
            raise SceneError(f"no viewpoint named '{name}'")
        return found

    def region_of(self, name: str, t: float = 0.0) -> Aabb:
        entity = self.entity(name)
        position, orientation = entity.pose_at(t)
        region = region_of_shape(entity.shape, position, orientation)
        if self.profile == "2d":
            region = _flatten_z(region)
        return region

    def centre_of(self, name: str, t: float = 0.0) -> Vec3:
        region = self.region_of(name, t)
        result = region.centre()
        return result

    def has_front(self, name: str) -> bool:
        entity = self.entity(name)
        result = self.ontology.has_front(entity.type)
        return result

    def select(self, selector: dict) -> tuple[str, ...]:
        """Selectors resolve to names. Coverage claims need this, or a model 'solves' a scene by deleting objects."""
        names = tuple(self.entities.keys())
        wanted_type = selector.get("type")
        if wanted_type is not None:
            names = tuple(n for n in names if _is_a(self, n, wanted_type))
        listed = selector.get("names")
        if listed is not None:
            names = tuple(n for n in listed if n in self.entities)
        return names

    def is_ordinal_timebase(self) -> bool:
        result = self.timebase == "steps"
        return result


def _is_a(scene: Scene, name: str, wanted: str) -> bool:
    entity = scene.entity(name)
    current: str | None = entity.type
    defs = scene.ontology.defs
    while current is not None:
        if current == wanted:
            return True
        definition = defs.get(current)
        if definition is None:
            return False
        current = definition.parent
    return False


PLANE_HALF = 1.0e6  # a 2D scene lives in the XY plane; give Z an unbounded span so it never binds (C1).


def _flatten_z(region: Aabb) -> Aabb:
    """In the 2D profile the canonical plane is XY viewed from +Z (C1). Z is degenerate — remove it from
    every topology/distance test by making the Z span cover everything, so only X and Y ever decide."""
    lo = (region.lo[0], region.lo[1], -PLANE_HALF)
    hi = (region.hi[0], region.hi[1], PLANE_HALF)
    result = Aabb(lo, hi)
    return result


def region_of_shape(shape: dict, position: Vec3, orientation: Quat) -> Aabb:
    kind = shape.get("kind")
    if kind == "box":
        extent = tuple(shape["extent"])
        result = box_region(position, orientation, extent)
    elif kind == "sphere":
        result = sphere_region(position, float(shape["radius"]))
    elif kind == "point":
        result = point_region(position)
    else:
        raise SceneError(f"unknown shape kind '{kind}'")
    return result


def _interpolate(keyframes: tuple[Keyframe, ...], t: float) -> tuple[Vec3, Quat]:
    ordered = sorted(keyframes, key=lambda k: k.t)
    first = ordered[0]
    last = ordered[-1]
    if t <= first.t:
        return (first.position, first.orientation)
    if t >= last.t:
        return (last.position, last.orientation)
    for index in range(1, len(ordered)):
        after = ordered[index]
        if after.t < t:
            continue
        before = ordered[index - 1]
        span = after.t - before.t
        u = 0.0 if span == 0.0 else (t - before.t) / span
        position = vm.lerp(before.position, after.position, u)
        orientation = before.orientation if u < 0.5 else after.orientation
        return (position, orientation)
    return (last.position, last.orientation)
