# Time: keyframed poses, HOLD as a sampled invariant, Allen over events — and the ordinal-timebase type error (C3).

from __future__ import annotations

from checker import check_scene

# A ball rolls from x=-2 to x=+2, passing under the desk top but never touching it.
ROLLING_BALL = {
    "name": "ball",
    "type": "ball",
    "shape": {"kind": "sphere", "radius": 0.1},
    "keyframes": [
        {"t": 0.0, "position": [-2.0, 0.0, 0.1]},
        {"t": 2.0, "position": [2.0, 0.0, 0.1]},
    ],
}

DESK = {
    "name": "desk",
    "type": "desk",
    "shape": {"kind": "box", "extent": [1.6, 0.8, 0.75]},
    "position": [0.0, 0.0, 1.0],  # raised: the ball rolls underneath, clear of it
}


def scene_with(claims, timebase="seconds", make_scene=None):
    result = make_scene(claims, entities=[DESK, ROLLING_BALL], viewpoints=[], timebase=timebase)
    return result


def test_pose_is_interpolated_at_the_stated_instant(make_scene):
    claim = {
        "pred": "DIR",
        "fig": "ball",
        "gnd": "desk",
        "term": "west",
        "at": 0.5,
        "text": "at 0.5s the ball is west of the desk",
    }
    scene = scene_with([claim], make_scene=make_scene)
    report = check_scene(scene)
    assert report.verdicts[0].status == "PASS"  # at t=0.5s the ball is still at x=-1


def test_the_same_claim_fails_later(make_scene):
    claim = {"pred": "DIR", "fig": "ball", "gnd": "desk", "term": "west", "at": 1.5}
    scene = scene_with([claim], make_scene=make_scene)
    report = check_scene(scene)
    assert report.verdicts[0].status == "FAIL"  # by t=1.5s it is east of the desk


def test_hold_is_a_sampled_invariant(make_scene):
    claim = {
        "pred": "HOLD",
        "interval": [0.0, 2.0],
        "claim": {"pred": "TOP", "a": "ball", "b": "desk", "rcc": ["DC"]},
        "text": "the ball is clear of the desk, held for 2s",
    }
    scene = scene_with([claim], make_scene=make_scene)
    report = check_scene(scene)
    assert report.verdicts[0].status == "PASS"


def test_hold_reports_where_it_broke(make_scene):
    claim = {
        "pred": "HOLD",
        "interval": [0.0, 2.0],
        "claim": {"pred": "DIR", "fig": "ball", "gnd": "desk", "term": "west"},
    }
    scene = scene_with([claim], make_scene=make_scene)
    report = check_scene(scene)
    verdict = report.verdicts[0]
    assert verdict.status == "FAIL"
    assert "broke at t=" in verdict.detail


def test_hold_on_an_ordinal_timebase_is_a_type_error(make_scene):
    """A 'steps' timebase carries order, not duration. Asking it to hold for 2s is a type error, not a false claim."""
    claim = {
        "pred": "HOLD",
        "interval": [0.0, 2.0],
        "claim": {"pred": "TOP", "a": "ball", "b": "desk", "rcc": ["DC"]},
    }
    scene = scene_with([claim], timebase="steps", make_scene=make_scene)
    report = check_scene(scene)
    verdict = report.verdicts[0]
    assert verdict.status == "ERROR"
    assert "ordinal" in verdict.detail


def test_allen_orders_events(make_scene):
    claim = {"pred": "ALLEN", "a": "touch_shelf", "b": "touch_floor", "rel": "before|meets"}
    scene = make_scene(
        [claim],
        entities=[DESK, ROLLING_BALL],
        viewpoints=[],
        events={"touch_shelf": [1.0, 1.02], "touch_floor": [1.5, 1.52]},
    )
    report = check_scene(scene)
    assert report.verdicts[0].status == "PASS"
