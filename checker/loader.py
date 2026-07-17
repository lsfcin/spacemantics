# JSON scene -> Scene IR. Declarations are mandatory: no frame, no units, no tolerance means no parse (SPEC §0).

from __future__ import annotations

import json
from pathlib import Path

from . import units as u
from .scene import Entity, Keyframe, Scene, SceneError, Tolerance, Viewpoint
from .types import TypeDef, base_ontology
from .vecmath import IDENTITY

CANONICAL_FRAME: dict[str, str] = {"handedness": "right", "up": "+Z", "forward": "+Y"}
TIMEBASES: frozenset[str] = frozenset({"seconds", "steps", "months", "frames"})


def load_scene(path: str | Path) -> Scene:
    text = Path(path).read_text(encoding="utf-8")
    document = json.loads(text)
    result = scene_from(document)
    return result


def scene_from(document: dict) -> Scene:
    _require_frame(document)
    scene = Scene(
        profile=_required(document, "profile"),
        timebase=_timebase(document),
        tolerance=_tolerance(document),
        units=_unit_context(document),
        ontology=_ontology(document),
        claims=tuple(document.get("claims", ())),
    )
    _load_entities(scene, document)
    _load_viewpoints(scene, document)
    _load_events(scene, document)
    return scene


def _required(document: dict, key: str) -> str:
    value = document.get(key)
    if value is None:
        raise SceneError(f"the document header must declare '{key}' — nothing is implicit (SPEC §0)")
    return str(value)


def _require_frame(document: dict) -> None:
    """Relations are only ever evaluated in canonical form; an adapter converts, the checker does not (C1)."""
    frame = document.get("frame")
    if frame is None:
        raise SceneError("the document header must declare 'frame' (C1)")
    for key, expected in CANONICAL_FRAME.items():
        found = frame.get(key)
        if found != expected:
            raise SceneError(
                f"frame.{key} is '{found}', canonical is '{expected}'. "
                f"The checker evaluates canonical form only — convert at the adapter (C1)."
            )


def _timebase(document: dict) -> str:
    declared = document.get("timebase", "seconds")
    base = str(declared).split("@")[0]
    if base not in TIMEBASES:
        raise SceneError(f"unknown timebase '{declared}' (C3)")
    return base


def _tolerance(document: dict) -> Tolerance:
    declared = document.get("tolerance")
    if declared is None:
        raise SceneError("tolerance is not optional: without it nothing is verifiable (SPEC §0)")
    length_q = u.parse_quantity(declared["length"])
    length = length_q.to_metres(u.UnitContext())
    angle_value, angle_unit = u.parse(declared["angle"])
    angle = u.angle_to_radians(angle_value, angle_unit)
    time = _tolerance_time(declared)
    return Tolerance(length=length, angle=angle, time=time)


def _tolerance_time(declared: dict) -> float:
    text = declared.get("time", "1ms")
    value, unit = u.parse(text)
    result = u.time_to_seconds(value, unit)
    return result


def _unit_context(document: dict) -> u.UnitContext:
    declared = document.get("units", {})
    context = u.UnitContext(
        dpi=declared.get("dpi"),
        cell_size_m=declared.get("cell_size_m"),
        parent_extent_m=declared.get("parent_extent_m"),
    )
    return context


def _ontology(document: dict):
    ontology = base_ontology()
    for declared in document.get("types", ()):
        definition = TypeDef(
            name=declared["name"],
            parent=declared.get("parent", "thing"),
            has_front=declared.get("has_front"),
        )
        ontology.add(definition)
    return ontology


def _load_entities(scene: Scene, document: dict) -> None:
    for declared in document.get("entities", ()):
        name = declared["name"]
        entity = Entity(
            name=name,
            type=declared["type"],
            shape=declared["shape"],
            position=tuple(declared.get("position", (0.0, 0.0, 0.0))),
            orientation=tuple(declared.get("orientation", IDENTITY)),
            keyframes=_keyframes(declared),
            free=frozenset(declared.get("free", ())),
        )
        scene.entities[name] = entity


def _keyframes(declared: dict) -> tuple[Keyframe, ...]:
    frames = []
    for raw in declared.get("keyframes", ()):
        frame = Keyframe(
            t=float(raw["t"]),
            position=tuple(raw["position"]),
            orientation=tuple(raw.get("orientation", IDENTITY)),
        )
        frames.append(frame)
    return tuple(frames)


def _load_viewpoints(scene: Scene, document: dict) -> None:
    for declared in document.get("viewpoints", ()):
        name = declared["name"]
        viewpoint = Viewpoint(
            name=name,
            position=tuple(declared["position"]),
            look_at=declared["look_at"],
        )
        scene.viewpoints[name] = viewpoint


def _load_events(scene: Scene, document: dict) -> None:
    for name, span in document.get("events", {}).items():
        scene.events[name] = (float(span[0]), float(span[1]))
