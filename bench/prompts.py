# The three message builders (task prompt, blind-retry nudge, checker feedback) and the pose extractor.

from __future__ import annotations

import json

from checker import PASS, CheckReport

FRAME_NOTE = (
    "Frame: right-handed, +Z up, +Y forward, +X east/right; units meters. "
    "Orientation is a unit quaternion [w,x,y,z]; use [1,0,0,0] for no rotation."
)


def build_task_prompt(task: dict) -> str:
    """The shared first prompt. Asks for a JSON pose per placeable entity — the format both arms use."""
    place = task["place"]
    movable = [_describe(e) for e in task["entities"] if e["name"] in place]
    fixed = [_describe_fixed(e) for e in task["entities"] if e.get("fixed")]
    lines = [
        "You place 3D objects in a scene.",
        FRAME_NOTE,
        "",
        f"Task: {task['prompt']}",
        "",
        "Objects you must place: " + "; ".join(movable) + ".",
    ]
    if fixed:
        one = "Already-fixed objects (do not move; given for reference): " + "; ".join(fixed) + "."
        lines.append(one)
    lines.append("")
    lines.append(
        'Output ONLY a JSON object mapping each object-to-place name to '
        '{"position":[x,y,z],"orientation":[w,x,y,z]}. No prose, no markdown fences.'
    )
    result = "\n".join(lines)
    return result


def build_blind_retry(previous: str) -> str:
    """The control nudge: another attempt, but with NO checker information — isolates 'more tries'."""
    result = (
        "That placement did not fully satisfy the task. Try again. "
        "Output ONLY the corrected JSON object, same format as before."
    )
    return result


def build_feedback(report: CheckReport) -> str:
    """The WITH-texpace signal: the checker's per-claim verdicts. This is the product under test."""
    lines = ["The checker evaluated your placement. These requirements are NOT yet met:"]
    for verdict in report.verdicts:
        if verdict.status == PASS:
            continue
        lines.append(f"- {verdict.text} [{verdict.status}]: {verdict.detail}")
    lines.append("")
    lines.append("Fix only what is needed. Output ONLY the full corrected JSON object, same format.")
    result = "\n".join(lines)
    return result


def extract_poses(text: str) -> dict:
    """Pull the JSON pose map out of a completion, tolerating markdown fences and surrounding prose."""
    body = _strip_to_json(text)
    parsed = json.loads(body)
    poses = {}
    for name, pose in parsed.items():
        if isinstance(pose, dict) and "position" in pose:
            poses[name] = pose
    return poses


def _strip_to_json(text: str) -> str:
    cleaned = text.strip()
    if "```" in cleaned:
        segments = cleaned.split("```")
        cleaned = max(segments, key=len)
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON object found in: {text[:120]}")
    result = cleaned[start : end + 1]
    return result


def _describe(entity: dict) -> str:
    result = f"{entity['name']} ({_shape(entity['shape'])})"
    return result


def _describe_fixed(entity: dict) -> str:
    result = f"{entity['name']} ({_shape(entity['shape'])}) at position {entity['position']}"
    return result


def _shape(shape: dict) -> str:
    if shape["kind"] == "box":
        result = f"box {shape['extent']} m"
    elif shape["kind"] == "sphere":
        result = f"sphere radius {shape['radius']} m"
    else:
        result = shape["kind"]
    return result
