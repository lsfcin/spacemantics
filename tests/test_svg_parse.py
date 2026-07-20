# SVG round-trip: the emitter's output parses back to the same positions, and plain metre-unit SVG parses too.

from __future__ import annotations

import json
from pathlib import Path

from adapters import parse_poses, render_document

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

PLAIN_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -5 10 10">
  <rect id="card" x="-2" y="-1.5" width="4" height="3"/>
  <circle id="dot" cx="1.0" cy="-2.0" r="0.25"/>
</svg>
"""


def test_emitter_output_round_trips_to_the_same_positions():
    """scene -> SVG -> parse must recover every entity's (x, y). The emitter writes 0.1-px coordinates,
    so recovery is exact to ~1 mm — assert 5 mm, an order under the checker's own 3-5 cm tolerance."""
    document = json.loads((EXAMPLES / "office.json").read_text(encoding="utf-8"))
    svg = render_document(document, "round-trip")
    poses = parse_poses(svg)
    for entity in document["entities"]:
        recovered = poses[entity["name"]]["position"]
        assert abs(recovered[0] - entity["position"][0]) < 0.005
        assert abs(recovered[1] - entity["position"][1]) < 0.005


def test_plain_svg_uses_the_metre_contract_with_y_flip():
    """Model-emitted SVG: 1 unit = 1 m, scene y = -svg y. Rect centre and circle centre both recovered."""
    poses = parse_poses(PLAIN_SVG)
    assert poses["card"]["position"] == [0.0, 0.0, 0.0]
    assert poses["dot"]["position"] == [1.0, 2.0, 0.0]


def test_prose_and_fences_around_the_svg_are_tolerated():
    wrapped = "Here is the drawing:\n```svg\n" + PLAIN_SVG + "\n```\nDone."
    poses = parse_poses(wrapped)
    assert set(poses) == {"card", "dot"}


def test_a_completion_with_no_svg_is_a_value_error():
    try:
        parse_poses("no drawing here")
        raised = False
    except ValueError:
        raised = True
    assert raised
