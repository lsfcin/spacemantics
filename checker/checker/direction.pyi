from . import allen as allen
from .geometry import interval_along as interval_along
from .scene import Scene as Scene
from .vecmath import UP as UP, Vec3 as Vec3

WORLD_TERMS: dict[str, Vec3]
PROJECTIVE_TERMS: frozenset[str]

class AnchorError(Exception): ...

def axis_for(term: str, anchor: dict, scene: Scene, ground: str, t: float) -> Vec3: ...
def holds(scene: Scene, figure: str, ground: str, term: str, anchor: dict, t: float = 0.0) -> tuple[bool, str]: ...
