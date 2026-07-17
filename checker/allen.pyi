Interval = tuple[float, float]
RELATIONS: tuple[str, ...]
INVERSE: dict[str, str]
BEYOND: frozenset[str]

def relation(a: Interval, b: Interval, eps: float) -> str: ...
def holds(a: Interval, b: Interval, expected: str, eps: float) -> bool: ...
