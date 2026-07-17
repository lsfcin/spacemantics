# Coverage and negation: without them a checker gets gamed (a baseline "solved" scenes by deleting objects).

from __future__ import annotations

from checker import check_scene


def only(scene):
    report = check_scene(scene)
    return report.verdicts[0]


NO_TWO_OVERLAP = {
    "quant": "none",
    "over": {"pairs": {"type": "thing"}},
    "pred": {"pred": "TOP", "rcc": ["PO", "EQ", "TPP", "TPPi", "NTPP", "NTPPi"]},
    "text": "no two objects overlap",
}


def test_no_two_objects_overlap(make_scene):
    scene = make_scene([NO_TWO_OVERLAP])
    verdict = only(scene)
    assert verdict.status == "PASS"


def test_an_overlap_is_caught_with_its_witness(make_scene, ):
    intruder = {
        "name": "crate",
        "type": "crate",
        "shape": {"kind": "box", "extent": [0.4, 0.4, 0.4]},
        "position": [0.0, 0.0, 0.5],  # driven straight through the desk
    }
    entities = _entities_plus(intruder)
    scene = make_scene([NO_TWO_OVERLAP], entities=entities)
    verdict = only(scene)
    assert verdict.status == "FAIL"
    assert "witness" in verdict.detail
    assert "crate" in verdict.detail


def test_count_stops_the_delete_everything_strategy(make_scene):
    scene = make_scene([{"pred": "COUNT", "set": {"type": "furniture"}, "op": "==", "n": 2}])
    verdict = only(scene)
    assert verdict.status == "PASS"
    scene = make_scene([{"pred": "COUNT", "set": {"type": "furniture"}, "op": "==", "n": 3}])
    verdict = only(scene)
    assert verdict.status == "FAIL"


def test_every_binds_the_figure_over_a_set(make_scene):
    claim = {
        "quant": "every",
        "over": {"set": {"type": "furniture"}, "as": "a"},
        "pred": {"pred": "TOP", "b": "ball", "rcc": ["DC"]},
        "text": "every piece of furniture is clear of the ball",
    }
    scene = make_scene([claim])
    verdict = only(scene)
    assert verdict.status == "PASS"


def _entities_plus(extra: dict) -> list[dict]:
    from conftest import ENTITIES

    entities = list(ENTITIES)
    entities.append(extra)
    return entities
