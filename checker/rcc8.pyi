from .geometry import Aabb as Aabb

CODES: tuple[str, ...]
PROSE: dict[str, tuple[str, ...]]

def relation(a: Aabb, b: Aabb, eps: float) -> str: ...
def holds(a: Aabb, b: Aabb, expected: tuple[str, ...], eps: float) -> tuple[bool, str]: ...
