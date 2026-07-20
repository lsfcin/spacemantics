# adapters
> Render a texpace scene to a viewable open format. SVG first — 2D, needs no engine, opens in any browser.
> spec: none
> goal: [spacemantics](../../../brain/goals/spacemantics.md)

The "recognized viewer" side of the project: texpace owns geometric *truth* via the checker; an adapter
turns a scene into something a **human can look at**. Renders are never scored — they exist so a person can
eyeball what the checker verified (the visual eyeball gate).

## What it does now

`render_document(document, title)` → an SVG string: top-down footprints of every entity (box → rect,
sphere → circle) with the **checker's verdicts drawn on** — any object that breaks a claim is red, and a
side panel lists each claim PASS/FAIL. So the picture *shows* what the checker caught.

```bash
python -m adapters ../examples/office.json          # scene JSON -> SVG on stdout
```

`render_pair(...)` puts two scenes side by side — e.g. a raw layout vs a checker-verified one (the
WITH/WITHOUT visual).

## Files

| File | Owns |
|---|---|
| [svg.py](svg.py) | scene → SVG: 2D projection, footprints, verdict colouring + panel; invertible (`id` per shape + `data-*` frame metadata) |
| [svg_parse.py](svg_parse.py) | SVG → poses: the round-trip. Emitter output inverted exactly; model-emitted SVG read under the metre contract (1 unit = 1 m, y flipped) |
| [__main__.py](__main__.py) | `python -m adapters <scene.json>` |

`parse_poses(text)` tolerates prose/fences around the SVG and returns `{name: {position, orientation}}`
for every `<rect>`/`<circle>` carrying an `id`. This is what lets the bench's raw-SVG arm be scored by
the checker (see [bench/CONTEXT.md](../bench/CONTEXT.md)).

## Honest scope

- **2D top-down only** today. A 3D scene is projected to its XY footprints — fine for planar layouts (UI,
  floor plans, iso maps); a real 3D view (isometric / glTF) is later work.
- The parser reads **positions, not sizes**: scoring takes shapes from the task spec. A full SVG→scene
  round-trip that also recovers extents (the cross-format consistency test) is still owed.

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`__init__.py`](__init__.py) | — | — | **facade** — adapters facade: render a texpace scene to a viewable open format, and parse one back for scoring. |
| [`__main__.py`](__main__.py) | — | `main` | CLI: `python -m adapters <scene.json>` -> an SVG (footprints + checker verdicts) on stdout. |
| [`svg.py`](svg.py) | — | `render_document`, `render_pair` | texpace scene -> SVG. Top-down footprints (x,y) with the checker's verdicts drawn on: red = a claim this object breaks. |
| [`svg_parse.py`](svg_parse.py) | — | `parse_poses`, `invert` | SVG -> poses: read per-object placements back out of an SVG so the checker can score raw-SVG output. |
<!-- routing:end -->
