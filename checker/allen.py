# Allen's 13 interval relations, with an explicit epsilon. Used twice: over time (tau) and per axis (Rectangle Algebra).

from __future__ import annotations

Interval = tuple[float, float]

RELATIONS: tuple[str, ...] = (
    "before",
    "meets",
    "overlaps",
    "starts",
    "during",
    "finishes",
    "equals",
    "finished_by",
    "contains",
    "started_by",
    "overlapped_by",
    "met_by",
    "after",
)

INVERSE: dict[str, str] = {
    "before": "after",
    "meets": "met_by",
    "overlaps": "overlapped_by",
    "starts": "started_by",
    "during": "contains",
    "finishes": "finished_by",
    "equals": "equals",
    "after": "before",
    "met_by": "meets",
    "overlapped_by": "overlaps",
    "started_by": "starts",
    "contains": "during",
    "finished_by": "finishes",
}

# The relations that place A wholly on the far side of B, i.e. "A is beyond B along this axis".
BEYOND: frozenset[str] = frozenset({"after", "met_by"})


def relation(a: Interval, b: Interval, eps: float) -> str:
    """The single Allen relation holding between A and B within tolerance eps."""
    starts_together = abs(a[0] - b[0]) <= eps
    ends_together = abs(a[1] - b[1]) <= eps
    if starts_together and ends_together:
        return "equals"
    if abs(a[1] - b[0]) <= eps:
        return "meets"
    if abs(b[1] - a[0]) <= eps:
        return "met_by"
    if a[1] < b[0]:
        return "before"
    if b[1] < a[0]:
        return "after"
    if starts_together:
        result = "starts" if a[1] < b[1] else "started_by"
        return result
    if ends_together:
        result = "finishes" if a[0] > b[0] else "finished_by"
        return result
    if a[0] > b[0] and a[1] < b[1]:
        return "during"
    if b[0] > a[0] and b[1] < a[1]:
        return "contains"
    if a[0] < b[0]:
        return "overlaps"
    return "overlapped_by"


def holds(a: Interval, b: Interval, expected: str, eps: float) -> bool:
    """Whether the named Allen relation holds. `expected` may be a disjunction: 'before|meets'."""
    found = relation(a, b, eps)
    wanted = expected.split("|")
    result = found in wanted
    return result
