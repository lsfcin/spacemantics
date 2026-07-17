# Unit-tagged quantities: five unit kinds, canonicalization to metres/seconds, and the ordinal type error (C2, C3).

from __future__ import annotations

import math
from dataclasses import dataclass

METRIC: dict[str, float] = {"m": 1.0, "mm": 0.001, "cm": 0.01, "km": 1000.0}
DEVICE: dict[str, float] = {"px": 1.0, "pt": 1.0, "emu": 1.0}
GRID: set[str] = {"cell", "voxel", "tile"}
NORMALIZED: set[str] = {"frac", "%"}
ORDINAL: set[str] = {"rank", "zindex", "reldepth", "step"}
ANGLE: dict[str, float] = {"rad": 1.0, "deg": math.pi / 180.0}
TIME: dict[str, float] = {"s": 1.0, "ms": 0.001, "min": 60.0}


class UnitTypeError(Exception):
    """An ordinal quantity reached a metric predicate, or a unit needs an undeclared conversion."""


@dataclass(frozen=True)
class UnitContext:
    """What a document must declare before non-metric units carry a magnitude at all."""

    dpi: float | None = None
    cell_size_m: float | None = None
    parent_extent_m: float | None = None


def kind_of(unit: str) -> str:
    if unit in METRIC:
        kind = "metric"
    elif unit in DEVICE:
        kind = "device"
    elif unit in GRID:
        kind = "grid"
    elif unit in NORMALIZED:
        kind = "normalized"
    elif unit in ORDINAL:
        kind = "ordinal"
    else:
        raise UnitTypeError(f"unknown unit '{unit}'")
    return kind


@dataclass(frozen=True)
class Quantity:
    """A length. There is no bare scalar length in texpace (C2)."""

    value: float
    unit: str

    def kind(self) -> str:
        result = kind_of(self.unit)
        return result

    def to_metres(self, ctx: UnitContext) -> float:
        """Canonical magnitude in metres. Ordinal quantities have none — that is a type error, not a wrong answer."""
        kind = self.kind()
        if kind == "ordinal":
            raise UnitTypeError(
                f"'{self.unit}' is ordinal: it carries rank, not magnitude, "
                f"and may never appear in a metric predicate (C2)"
            )
        if kind == "metric":
            result = self.value * METRIC[self.unit]
        elif kind == "device":
            result = _device_to_metres(self.value, self.unit, ctx)
        elif kind == "grid":
            result = _grid_to_metres(self.value, ctx)
        else:
            result = _normalized_to_metres(self.value, self.unit, ctx)
        return result


def _device_to_metres(value: float, unit: str, ctx: UnitContext) -> float:
    if ctx.dpi is None:
        raise UnitTypeError(f"'{unit}' is a device unit: declare a dpi/viewport before using it metrically")
    if unit == "emu":
        result = value / 914400.0 * 0.0254
    elif unit == "pt":
        result = value / 72.0 * 0.0254
    else:
        result = value / ctx.dpi * 0.0254
    return result


def _grid_to_metres(value: float, ctx: UnitContext) -> float:
    if ctx.cell_size_m is None:
        raise UnitTypeError("grid units need the cell's physical size declared (C2)")
    result = value * ctx.cell_size_m
    return result


def _normalized_to_metres(value: float, unit: str, ctx: UnitContext) -> float:
    if ctx.parent_extent_m is None:
        raise UnitTypeError("normalized units need the parent extent declared (C2)")
    fraction = value / 100.0 if unit == "%" else value
    result = fraction * ctx.parent_extent_m
    return result


def parse(text: str) -> tuple[float, str]:
    """'5mm' -> (5.0, 'mm'). A bare number does not parse: there is no untagged length (C2)."""
    stripped = text.strip()
    digits = ""
    for index, character in enumerate(stripped):
        legal = character.isdigit() or character in "+-."
        if not legal:
            break
        digits += character
    unit = stripped[len(digits) :].strip()
    if not digits or not unit:
        raise UnitTypeError(f"'{text}' is not a unit-tagged quantity (write e.g. '5mm', not '5')")
    value = float(digits)
    return (value, unit)


def parse_quantity(text: str) -> Quantity:
    value, unit = parse(text)
    return Quantity(value, unit)


def angle_to_radians(value: float, unit: str) -> float:
    if unit not in ANGLE:
        raise UnitTypeError(f"'{unit}' is not an angle unit")
    result = value * ANGLE[unit]
    return result


def time_to_seconds(value: float, unit: str) -> float:
    if unit not in TIME:
        raise UnitTypeError(f"'{unit}' is not an SI time unit; frames/steps/months convert at the adapter (C3)")
    result = value * TIME[unit]
    return result
