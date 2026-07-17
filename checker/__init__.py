# texpace checker facade: the only import surface. Load a scene, score its claims, read the report.

from __future__ import annotations

from .direction import AnchorError
from .evaluate import check_scene
from .loader import load_scene, scene_from
from .metrics import PredicateError
from .report import ERROR, FAIL, PASS, SKIPPED, CheckReport, Verdict
from .scene import Entity, Scene, SceneError, Tolerance, Viewpoint
from .types import Ontology, TypeDef, base_ontology
from .units import Quantity, UnitContext, UnitTypeError

__all__ = [
    "AnchorError",
    "CheckReport",
    "Entity",
    "ERROR",
    "FAIL",
    "Ontology",
    "PASS",
    "PredicateError",
    "Quantity",
    "SKIPPED",
    "Scene",
    "SceneError",
    "Tolerance",
    "TypeDef",
    "UnitContext",
    "UnitTypeError",
    "Verdict",
    "Viewpoint",
    "base_ontology",
    "check_scene",
    "load_scene",
    "scene_from",
]
