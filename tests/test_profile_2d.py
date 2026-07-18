# The 2D profile: the plane is XY viewed from +Z, so "above" means +Y and topology ignores the degenerate Z (C1).

from __future__ import annotations

from checker import check_scene, scene_from

HDR_2D = {
    "texpace": "1.0",
    "profile": "2d",
    "frame": {"handedness": "right", "up": "+Z", "forward": "+Y", "origin": "datum"},
    "units": {"length": "m", "angle": "rad"},
    "timebase": "seconds",
    "tolerance": {"length": "3cm", "angle": "10deg", "time": "1ms"},
}


def widget(name, extent, position):
    result = {"name": name, "type": "crate", "shape": {"kind": "box", "extent": extent}, "position": position}
    return result


def build(entities, claims):
    document = dict(HDR_2D)
    document["entities"] = entities
    document["claims"] = claims
    scene = scene_from(document)
    report = check_scene(scene)
    return report


def test_above_is_plus_y_in_2d():
    """A UI title above a button: 'above' is +Y here, not gravity — the thin Z must not decide it."""
    entities = [widget("title", [3.6, 0.5, 0.01], [0, 1.0, 0]), widget("button", [1.2, 0.5, 0.01], [0, -1.0, 0])]
    claim = {"pred": "DIR", "fig": "title", "gnd": "button", "term": "above", "anchor": {"kind": "world"}}
    report = build(entities, [claim])
    assert report.verdicts[0].status == "PASS"


def test_thin_containment_survives_tolerance_in_2d():
    """A thin card + thin title: in 3D the 1cm Z would read as EC under a 3cm tolerance; in 2D it is NTPP."""
    entities = [widget("card", [4, 3, 0.01], [0, 0, 0]), widget("title", [3.6, 0.5, 0.01], [0, 1.0, 0])]
    claim = {"pred": "TOP", "a": "title", "b": "card", "rcc": ["TPP", "NTPP"], "text": "title within card"}
    report = build(entities, [claim])
    assert report.verdicts[0].status == "PASS"


def test_planar_overlap_still_caught_in_2d():
    """Flattening Z must not hide a genuine XY overlap."""
    entities = [widget("button", [1.2, 0.5, 0.01], [0, -1.0, 0]), widget("icon", [0.5, 0.5, 0.01], [0.4, -1.0, 0])]
    claim = {"pred": "TOP", "a": "button", "b": "icon", "rcc": ["PO"], "text": "button overlaps icon"}
    report = build(entities, [claim])
    assert report.verdicts[0].status == "PASS"


def test_3d_above_is_still_plus_z():
    """Regression guard: the 2D rule must not leak into 3D — there 'above' stays gravity (+Z)."""
    document = dict(HDR_2D)
    document["profile"] = "3d"
    document["entities"] = [widget("hi", [1, 1, 1], [0, 0, 2]), widget("lo", [1, 1, 1], [0, 0, 0])]
    document["claims"] = [{"pred": "DIR", "fig": "hi", "gnd": "lo", "term": "above", "anchor": {"kind": "world"}}]
    scene = scene_from(document)
    report = check_scene(scene)
    assert report.verdicts[0].status == "PASS"
