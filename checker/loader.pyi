from .scene import Entity as Entity, Keyframe as Keyframe, Scene as Scene, SceneError as SceneError, Tolerance as Tolerance, Viewpoint as Viewpoint
from .types import TypeDef as TypeDef, base_ontology as base_ontology
from .vecmath import IDENTITY as IDENTITY
from pathlib import Path

CANONICAL_FRAME: dict[str, str]
TIMEBASES: frozenset[str]

def load_scene(path: str | Path) -> Scene: ...
def scene_from(document: dict) -> Scene: ...
