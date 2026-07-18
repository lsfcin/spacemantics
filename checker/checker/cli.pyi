from .evaluate import check_scene as check_scene
from .loader import load_scene as load_scene
from .scene import SceneError as SceneError
from .units import UnitTypeError as UnitTypeError

def main(argv: list[str] | None = None) -> int: ...
