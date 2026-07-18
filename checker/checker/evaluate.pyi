from . import allen as allen, direction as direction, metrics as metrics, rcc8 as rcc8
from .report import CheckReport as CheckReport, ERROR as ERROR, FAIL as FAIL, PASS as PASS, SKIPPED as SKIPPED, Verdict as Verdict
from .scene import Scene as Scene
from .units import Quantity as Quantity, UnitTypeError as UnitTypeError

QUANTIFIERS: frozenset[str]

def check_scene(scene: Scene) -> CheckReport: ...
