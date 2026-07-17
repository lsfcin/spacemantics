# The header is mandatory: no frame, no tolerance, no non-canonical frames. Plus the user-extensible type ontology.

from __future__ import annotations

import pytest

from checker import SceneError, check_scene, scene_from
from conftest import ENTITIES, HEADER


def document_without(key: str) -> dict:
    document = dict(HEADER)
    document.pop(key)
    document["entities"] = ENTITIES
    return document


def test_a_missing_tolerance_does_not_parse():
    with pytest.raises(SceneError, match="tolerance is not optional"):
        scene_from(document_without("tolerance"))


def test_a_missing_frame_does_not_parse():
    with pytest.raises(SceneError, match="must declare 'frame'"):
        scene_from(document_without("frame"))


def test_a_non_canonical_frame_is_rejected_at_the_door():
    """glTF is Y-up. The adapter converts; the checker evaluates canonical form only (C1)."""
    document = dict(HEADER)
    document["frame"] = {"handedness": "right", "up": "+Y", "forward": "-Z"}
    document["entities"] = ENTITIES
    with pytest.raises(SceneError, match="canonical is"):
        scene_from(document)


def test_the_type_ontology_is_user_extensible(make_scene):
    """'a lectern is a kind of furniture' — and it inherits furniture's intrinsic front."""
    entities = [
        {"name": "lectern", "type": "lectern", "shape": {"kind": "box", "extent": [0.5, 0.4, 1.1]},
         "position": [0.0, 0.0, 0.55]},
        {"name": "chair", "type": "chair", "shape": {"kind": "box", "extent": [0.5, 0.5, 0.9]},
         "position": [0.0, 1.2, 0.45]},
    ]
    claim = {"pred": "DIR", "fig": "chair", "gnd": "lectern", "term": "front", "anchor": {"kind": "locale"}}
    scene = make_scene([claim], entities=entities, viewpoints=[], types=[{"name": "lectern", "parent": "furniture"}])
    report = check_scene(scene)
    assert report.verdicts[0].status == "PASS"


def test_free_dofs_are_reported_not_scored(make_scene):
    entities = [dict(entity) for entity in ENTITIES]
    entities[1]["free"] = ["position.z"]
    scene = make_scene([], entities=entities)
    report = check_scene(scene)
    assert report.free_dofs == ("chair.position.z",)
    assert "1 free DOF" in report.summary()
