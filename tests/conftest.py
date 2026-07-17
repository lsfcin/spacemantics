# Scene fixtures: a definite desk/chair/lamp/ball scene in canonical form, built through the loader.

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from checker import scene_from  # noqa: E402

HEADER = {
    "texpace": "1.0",
    "profile": "3d",
    "frame": {"handedness": "right", "up": "+Z", "forward": "+Y", "origin": "datum"},
    "units": {"length": "m", "angle": "rad"},
    "timebase": "seconds",
    "tolerance": {"length": "5mm", "angle": "0.5deg", "time": "1ms"},
}

# The desk faces +Y (identity orientation). Its front face is at y = +0.4.
ENTITIES = [
    {
        "name": "desk",
        "type": "desk",
        "shape": {"kind": "box", "extent": [1.6, 0.8, 0.75]},
        "position": [0.0, 0.0, 0.375],
    },
    {
        "name": "chair",
        "type": "chair",
        "shape": {"kind": "box", "extent": [0.5, 0.5, 0.9]},
        "position": [0.0, 0.9, 0.45],
        # Rotated a half-turn about +Z: the chair's front axis points back at the desk (-Y).
        "orientation": [0.0, 0.0, 0.0, 1.0],
    },
    {
        "name": "lamp",
        "type": "lamp",
        "shape": {"kind": "box", "extent": [0.2, 0.2, 0.4]},
        "position": [0.6, 0.0, 0.95],  # resting on the desk top (z = 0.75)
    },
    {
        "name": "ball",
        "type": "ball",
        "shape": {"kind": "sphere", "radius": 0.1},
        "position": [-2.0, 0.0, 0.1],
    },
]

VIEWPOINTS = [{"name": "door", "position": [0.0, 6.0, 1.6], "look_at": "desk"}]


def build(claims: list[dict], **overrides) -> object:
    document = dict(HEADER)
    document.update(overrides)
    document.setdefault("entities", ENTITIES)
    document.setdefault("viewpoints", VIEWPOINTS)
    document["claims"] = claims
    result = scene_from(document)
    return result


@pytest.fixture
def make_scene():
    return build


@pytest.fixture
def degrees():
    return math.degrees
