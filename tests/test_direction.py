# DIR under the three anchors, and the arity gate: an unreadable projective term is an ERROR, never a FAIL.

from __future__ import annotations

from checker import check_scene


def verdicts(scene):
    report = check_scene(scene)
    return report.verdicts


def test_world_anchor_needs_no_frame(make_scene):
    scene = make_scene(
        [
            {"pred": "DIR", "fig": "lamp", "gnd": "desk", "term": "above", "text": "the lamp is above the desk"},
            {"pred": "DIR", "fig": "ball", "gnd": "desk", "term": "west", "text": "the ball is west of the desk"},
        ]
    )
    found = verdicts(scene)
    assert [v.status for v in found] == ["PASS", "PASS"]


def test_locale_anchor_reads_the_grounds_own_front(make_scene):
    """'the chair is in front of the desk' = the desk's own front. The natural English reading."""
    scene = make_scene(
        [
            {
                "pred": "DIR",
                "fig": "chair",
                "gnd": "desk",
                "term": "front",
                "anchor": {"kind": "locale"},
                "text": "the chair is in front of the desk",
            }
        ]
    )
    found = verdicts(scene)
    assert found[0].status == "PASS"


def test_locale_on_a_frontless_ground_is_an_error(make_scene):
    """A ball has no front. texpace refuses to represent 'left of the ball' rather than guessing."""
    scene = make_scene(
        [
            {
                "pred": "DIR",
                "fig": "desk",
                "gnd": "ball",
                "term": "left",
                "anchor": {"kind": "locale"},
                "text": "the desk is left of the ball",
            }
        ]
    )
    found = verdicts(scene)
    assert found[0].status == "ERROR"
    assert "no intrinsic front" in found[0].detail


def test_projective_term_without_any_frame_is_an_error(make_scene):
    scene = make_scene(
        [{"pred": "DIR", "fig": "chair", "gnd": "desk", "term": "left", "anchor": {"kind": "world"}}]
    )
    found = verdicts(scene)
    assert found[0].status == "ERROR"


def test_group_anchor_uses_the_viewers_left(make_scene):
    """The viewer stands at +Y looking back at the desk, so world -X (the ball) is on the viewer's RIGHT.

    The same ball is 'west of the desk' in world terms. Same scene, two frames, two different true
    sentences — which is exactly why the frame must be declared and never inferred.
    """
    scene = make_scene(
        [
            {
                "pred": "DIR",
                "fig": "ball",
                "gnd": "desk",
                "term": "right",
                "anchor": {"kind": "group", "viewpoint": "door"},
                "text": "the ball is right of the desk seen from the door",
            },
            {
                "pred": "DIR",
                "fig": "ball",
                "gnd": "desk",
                "term": "left",
                "anchor": {"kind": "group", "viewpoint": "door"},
                "text": "the ball is left of the desk seen from the door",
            },
        ]
    )
    found = verdicts(scene)
    assert found[0].status == "PASS"
    assert found[1].status == "FAIL"


def test_a_lamp_on_the_desk_is_not_left_of_it(make_scene):
    """Rectangle Algebra is strict: 'left of' needs the intervals disjoint on the axis, not merely offset."""
    scene = make_scene(
        [
            {
                "pred": "DIR",
                "fig": "lamp",
                "gnd": "desk",
                "term": "left",
                "anchor": {"kind": "group", "viewpoint": "door"},
            }
        ]
    )
    found = verdicts(scene)
    assert found[0].status == "FAIL"


def test_group_anchor_without_a_viewpoint_is_an_error(make_scene):
    scene = make_scene([{"pred": "DIR", "fig": "chair", "gnd": "desk", "term": "left", "anchor": {"kind": "group"}}])
    found = verdicts(scene)
    assert found[0].status == "ERROR"
