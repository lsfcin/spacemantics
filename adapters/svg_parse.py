# SVG -> poses: read per-object placements back out of an SVG so the checker can score raw-SVG output.

from __future__ import annotations

from typing import Callable
from xml.etree import ElementTree

from .svg import PAD, TOP

IDENTITY = [1.0, 0.0, 0.0, 0.0]
Invert = Callable[[float, float], tuple[float, float]]


def parse_poses(text: str) -> dict:
    """Extract `{name: {"position", "orientation"}}` from SVG shapes carrying an `id`.

    Contract for model-emitted SVG: 1 SVG unit = 1 metre, scene (x, y) = (svg x, -svg y) — SVG y grows
    downward. Our own emitter's output (root carries data-minx/data-maxy/data-scale) is inverted exactly.
    Positions land on z=0, orientation identity — the 2D-profile checker flattens Z anyway (C1).
    """
    body = _strip_to_svg(text)
    root = _parse_xml(body)
    invert = _inverter(root)
    poses = {}
    for element in root.iter():
        entry = _pose_from(element, invert)
        if entry is not None:
            poses[entry[0]] = entry[1]
    return poses


def _strip_to_svg(text: str) -> str:
    start = text.find("<svg")
    end = text.rfind("</svg>")
    if start == -1 or end == -1:
        raise ValueError(f"no <svg> element found in: {text[:120]}")
    result = text[start : end + 6]
    return result


def _parse_xml(body: str) -> ElementTree.Element:
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError as failure:
        raise ValueError(f"invalid SVG: {failure}") from failure
    return root


def _inverter(root: ElementTree.Element) -> Invert:
    marked = root.get("data-scale")
    if marked is None:
        result = _plain_inverse
    else:
        result = _emitter_inverse(root)
    return result


def _plain_inverse(sx: float, sy: float) -> tuple[float, float]:
    result = (sx, -sy)
    return result


def _emitter_inverse(root: ElementTree.Element) -> Invert:
    minx = _get_float(root, "data-minx")
    maxy = _get_float(root, "data-maxy")
    scale = _get_float(root, "data-scale")

    def invert(sx: float, sy: float) -> tuple[float, float]:
        x = minx + (sx - PAD) / scale
        y = maxy - (sy - TOP) / scale
        result = (x, y)
        return result

    return invert


def _pose_from(element: ElementTree.Element, invert: Invert) -> tuple[str, dict] | None:
    tag = _local(element.tag)
    name = element.get("id")
    entry = None
    if tag in ("rect", "circle") and name:
        sx, sy = _center(element, tag)
        x, y = invert(sx, sy)
        pose = {"position": [x, y, 0.0], "orientation": list(IDENTITY)}
        entry = (name, pose)
    return entry


def _center(element: ElementTree.Element, tag: str) -> tuple[float, float]:
    if tag == "circle":
        sx = _get_float(element, "cx")
        sy = _get_float(element, "cy")
    else:
        x = _get_float(element, "x")
        y = _get_float(element, "y")
        w = _get_float(element, "width")
        h = _get_float(element, "height")
        sx = x + w / 2
        sy = y + h / 2
    return (sx, sy)


def _get_float(element: ElementTree.Element, attribute: str) -> float:
    raw = element.get(attribute, "0")
    result = float(raw)
    return result


def _local(tag: str) -> str:
    parts = tag.rsplit("}", 1)
    result = parts[-1]
    return result
