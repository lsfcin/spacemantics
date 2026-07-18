# texpace scene -> SVG. Top-down footprints (x,y) with the checker's verdicts drawn on: red = a claim this object breaks.

from __future__ import annotations

from checker import FAIL, PASS, check_scene, scene_from

PAD = 24
PANEL_W = 360
MAX_SCALE = 90.0
PASS_FILL, PASS_STROKE = "#cfe3ff", "#3b6fb0"
FAIL_FILL, FAIL_STROKE = "#ffd4d4", "#c0392b"
GREEN, RED, INK = "#1e7a34", "#c0392b", "#222"


def render_document(document: dict, title: str) -> str:
    """One scene: footprints + a verdict panel. Objects that break a claim are drawn red."""
    scene = scene_from(document)
    report = check_scene(scene)
    broken = _failing_entities(document, report)
    shapes = _project(document)
    body, width, height = _draw(shapes, broken, title, report)
    svg = _wrap(body, width, height)
    return svg


def render_pair(left: dict, right: dict, left_title: str, right_title: str) -> str:
    """Two scenes side by side — e.g. an unchecked layout vs a checker-verified one."""
    left_svg = render_document(left, left_title)
    right_svg = render_document(right, right_title)
    result = f'<div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start">{left_svg}{right_svg}</div>'
    return result


def _project(document: dict) -> list[dict]:
    shapes = []
    for entity in document.get("entities", []):
        shape = _footprint(entity)
        shapes.append(shape)
    return shapes


def _footprint(entity: dict) -> dict:
    position = entity.get("position", [0, 0, 0])
    cx, cy = float(position[0]), float(position[1])
    shape = entity["shape"]
    if shape["kind"] == "sphere":
        radius = float(shape["radius"])
        result = {"name": entity["name"], "kind": "circle", "cx": cx, "cy": cy, "w": radius, "h": radius}
    else:
        extent = shape.get("extent", [0.2, 0.2, 0.2])
        result = {"name": entity["name"], "kind": "rect", "cx": cx, "cy": cy, "w": float(extent[0]), "h": float(extent[1])}
    return result


def _bounds(shapes: list[dict]) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for shape in shapes:
        xs.extend([shape["cx"] - shape["w"], shape["cx"] + shape["w"]])
        ys.extend([shape["cy"] - shape["h"], shape["cy"] + shape["h"]])
    if not xs:
        return (-1.0, 1.0, -1.0, 1.0)
    return (min(xs), max(xs), min(ys), max(ys))


def _draw(shapes: list[dict], broken: set, title: str, report) -> tuple[str, int, int]:
    minx, maxx, miny, maxy = _bounds(shapes)
    world_w = max(maxx - minx, 0.5)
    world_h = max(maxy - miny, 0.5)
    scale = min(MAX_SCALE, 300.0 / world_w, 300.0 / world_h)
    draw_w = world_w * scale
    draw_h = world_h * scale
    elems = [f'<text x="{PAD}" y="18" font-size="15" font-weight="700" fill="{INK}">{_esc(title)}</text>']
    for shape in shapes:
        elems.append(_shape_svg(shape, minx, maxy, scale, shape["name"] in broken))
    panel_x = PAD + draw_w + 24
    elems.extend(_panel(report, panel_x))
    width = int(panel_x + PANEL_W)
    height = int(max(draw_h + 2 * PAD + 20, 40 + 22 * (len(report.verdicts) + 1)))
    body = "\n".join(elems)
    return (body, width, height)


def _shape_svg(shape: dict, minx: float, maxy: float, scale: float, is_broken: bool) -> str:
    fill = FAIL_FILL if is_broken else PASS_FILL
    stroke = FAIL_STROKE if is_broken else PASS_STROKE
    sx = PAD + (shape["cx"] - minx) * scale
    sy = 28 + (maxy - shape["cy"]) * scale
    label = f'<text x="{sx:.1f}" y="{sy:.1f}" font-size="11" text-anchor="middle" fill="{INK}">{_esc(shape["name"])}</text>'
    if shape["kind"] == "circle":
        radius = shape["w"] * scale
        body = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    else:
        w = shape["w"] * scale
        h = shape["h"] * scale
        rx = sx - w / 2
        ry = sy - h / 2
        body = f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    result = body + "\n" + label
    return result


def _panel(report, x: float) -> list[str]:
    lines = [f'<text x="{x:.0f}" y="18" font-size="13" font-weight="700" fill="{INK}">checker verdicts</text>']
    y = 40
    for verdict in report.verdicts:
        colour = GREEN if verdict.status == PASS else RED
        mark = "PASS" if verdict.status == PASS else verdict.status
        text = f'<text x="{x:.0f}" y="{y}" font-size="12" fill="{colour}">[{mark}] {_esc(verdict.text)}</text>'
        lines.append(text)
        y += 22
    total = len(report.verdicts)
    passed = sum(1 for v in report.verdicts if v.status == PASS)
    summary = f'<text x="{x:.0f}" y="{y + 6}" font-size="12" font-weight="700" fill="{INK}">{passed}/{total} claims pass</text>'
    lines.append(summary)
    return lines


def _failing_entities(document: dict, report) -> set:
    broken = set()
    claims = document.get("claims", [])
    for verdict, claim in zip(report.verdicts, claims):
        if verdict.status == PASS:
            continue
        names = _claim_entities(claim, document)
        broken.update(names)
    return broken


def _claim_entities(claim: dict, document: dict) -> set:
    names = set()
    for key in ("a", "b", "fig", "gnd"):
        value = claim.get(key)
        if isinstance(value, str):
            names.add(value)
    if "quant" in claim or claim.get("pred") == "COUNT":
        names.update(_set_members(claim, document))
    return names


def _set_members(claim: dict, document: dict) -> set:
    over = claim.get("over", {})
    selector = over.get("pairs") or over.get("set") or claim.get("set") or {}
    wanted = selector.get("type")
    members = set()
    for entity in document.get("entities", []):
        if wanted is None or entity["type"] == wanted:
            members.add(entity["name"])
    return members


def _wrap(body: str, width: int, height: int) -> str:
    result = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="background:#fff;border:1px solid #ddd;border-radius:8px">\n'
        f"{body}\n</svg>"
    )
    return result


def _esc(text: str) -> str:
    result = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return result
