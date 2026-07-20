from .svg import PAD as PAD, TOP as TOP
from _typeshed import Incomplete
from typing import Callable

IDENTITY: Incomplete
Invert = Callable[[float, float], tuple[float, float]]

def parse_poses(text: str) -> dict: ...
