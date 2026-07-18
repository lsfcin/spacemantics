from .geometry import Aabb as Aabb, box_region as box_region, point_region as point_region, sphere_region as sphere_region
from .types import Ontology as Ontology, base_ontology as base_ontology
from .units import UnitContext as UnitContext
from .vecmath import IDENTITY as IDENTITY, Quat as Quat, Vec3 as Vec3
from dataclasses import dataclass, field

class SceneError(Exception): ...

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
    position: Vec3 = ...
    orientation: Quat = ...
    keyframes: tuple[Keyframe, ...] = ...
    free: frozenset[str] = ...
    def pose_at(self, t: float) -> tuple[Vec3, Quat]: ...

@dataclass(frozen=True)
class Viewpoint:
    name: str
    position: Vec3
    look_at: str

@dataclass(frozen=True)
class Tolerance:
    length: float
    angle: float
    time: float = ...

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
    claims: tuple[dict, ...] = ...
    def entity(self, name: str) -> Entity: ...
    def viewpoint(self, name: str) -> Viewpoint: ...
    def region_of(self, name: str, t: float = 0.0) -> Aabb: ...
    def centre_of(self, name: str, t: float = 0.0) -> Vec3: ...
    def has_front(self, name: str) -> bool: ...
    def select(self, selector: dict) -> tuple[str, ...]: ...
    def is_ordinal_timebase(self) -> bool: ...

def region_of_shape(shape: dict, position: Vec3, orientation: Quat) -> Aabb: ...
