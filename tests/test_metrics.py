# DIST, faces, alignment — and the ordinal rule: rank may never enter a metric predicate (C2).

from __future__ import annotations

from checker import check_scene


def only(scene):
    report = check_scene(scene)
    return report.verdicts[0]


def test_distance_is_point_to_region(make_scene):
    """Schematized: the ball collapses to a point, the desk keeps its region. Centre-to-face = 1.2m."""
    scene = make_scene(
        [{"pred": "DIST", "fig": "ball", "gnd": "desk", "op": "<", "q": {"value": 1.5, "unit": "m"}}]
    )
    verdict = only(scene)
    assert verdict.status == "PASS"
    assert "distance=1.2000m" in verdict.detail


def test_distance_can_fail(make_scene):
    scene = make_scene(
        [{"pred": "DIST", "fig": "ball", "gnd": "desk", "op": "<", "q": {"value": 1.0, "unit": "m"}}]
    )
    verdict = only(scene)
    assert verdict.status == "FAIL"


def test_ordinal_quantity_in_a_metric_predicate_is_a_type_error(make_scene):
    """The load-bearing rule from C2: CV relative depth carries rank, not magnitude."""
    scene = make_scene(
        [{"pred": "DIST", "fig": "ball", "gnd": "desk", "op": "<", "q": {"value": 3, "unit": "reldepth"}}]
    )
    verdict = only(scene)
    assert verdict.status == "ERROR"
    assert "ordinal" in verdict.detail


def test_grid_units_need_a_declared_cell_size(make_scene):
    scene = make_scene(
        [{"pred": "DIST", "fig": "ball", "gnd": "desk", "op": "<", "q": {"value": 2, "unit": "cell"}}]
    )
    verdict = only(scene)
    assert verdict.status == "ERROR"
    scene = make_scene(
        [{"pred": "DIST", "fig": "ball", "gnd": "desk", "op": "<", "q": {"value": 2, "unit": "cell"}}],
        units={"length": "m", "angle": "rad", "cell_size_m": 1.5},
    )
    verdict = only(scene)
    assert verdict.status == "PASS"  # 2 cells = 3m > 1.2m


def test_faces_requires_a_front(make_scene):
    scene = make_scene([{"pred": "FACES", "a": "ball", "b": "desk"}])
    verdict = only(scene)
    assert verdict.status == "ERROR"
    assert "has no front" in verdict.detail


def test_chair_faces_the_desk(make_scene):
    """Centroid schematization means 'faces' carries the height offset; the declared angle tolerance absorbs it."""
    scene = make_scene(
        [{"pred": "FACES", "a": "chair", "b": "desk", "text": "the chair faces the desk"}],
        tolerance={"length": "5mm", "angle": "6deg", "time": "1ms"},
    )
    verdict = only(scene)
    assert verdict.status == "PASS"


def test_alignment_is_tolerance_bound(make_scene):
    scene = make_scene([{"pred": "ALIGNED", "a": "chair", "b": "desk", "axis": "x"}])
    verdict = only(scene)
    assert verdict.status == "PASS"
    scene = make_scene([{"pred": "ALIGNED", "a": "lamp", "b": "desk", "axis": "x"}])
    verdict = only(scene)
    assert verdict.status == "FAIL"


def test_chair_is_antiparallel_to_the_desk_hence_parallel(make_scene):
    scene = make_scene([{"pred": "PARALLEL", "a": "chair", "b": "desk"}])
    verdict = only(scene)
    assert verdict.status == "PASS"
