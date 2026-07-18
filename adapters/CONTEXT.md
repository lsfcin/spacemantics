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
| [svg.py](svg.py) | scene → SVG: 2D projection, footprints, verdict colouring + panel |
| [__main__.py](__main__.py) | `python -m adapters <scene.json>` |

## Honest scope

- **2D top-down only** today. A 3D scene is projected to its XY footprints — fine for planar layouts (UI,
  floor plans, iso maps); a real 3D view (isometric / glTF) is later work.
- **Emit only.** The round-trip parser (SVG → scene, needed to *score* a model's raw-SVG output in the
  WITHOUT arm) is the next piece — see [bench/CONTEXT.md](../bench/CONTEXT.md).
- The full model-driven WITH/WITHOUT (a model emitting raw SVG vs emitting texpace + checker feedback)
  needs an on-slate model; the render + score pipeline is what makes its two outputs comparable.

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`__init__.py`](__init__.py) | — | — | **facade** — adapters facade: render a texpace scene to a viewable open format. SVG first (2D, needs no engine). |
| [`__main__.py`](__main__.py) | — | `main` | CLI: `python -m adapters <scene.json>` -> an SVG (footprints + checker verdicts) on stdout. |
| [`svg.py`](svg.py) | — | `render_document`, `render_pair` | texpace scene -> SVG. Top-down footprints (x,y) with the checker's verdicts drawn on: red = a claim this object breaks. |
<!-- routing:end -->
