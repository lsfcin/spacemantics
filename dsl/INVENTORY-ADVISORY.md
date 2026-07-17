# texpace — Concept Inventory: advisory and out-of-scope
> Continuation of INVENTORY.md — the concepts the checkability filter did NOT admit to the kernel

See [INVENTORY.md](INVENTORY.md) for `core` + `module` concepts and the legend. Per-format capability is
in [CONFORMANCE.md](CONFORMANCE.md) §6.

- **`advisory`** = expressible and executable, but not deterministically checkable — or checkable only via
  *observable outcomes*. Scored only on those observables, if at all.
- **`out`** = out of scope for texpace.

This file is where the filter's teeth show. Nothing below was dropped for being unimportant; each was
demoted because no deterministic predicate could be written for it.

## Advisory concepts

| Concept | Source | Dimensions | Formats | Checkable? (how) |
|---|---|---|---|---|
| **Physics** (rigid-body dynamics, gravity, collision response) | brainstorm | 2.5D/3D/4D | none in core spec — engine-executed (Blender/Bullet) | **outcome-checked only**: spec states initial conditions + goal post-conditions; a recognized engine simulates; the checker verifies observables — rest positions, contact events, and their Allen ordering — within tolerance. Simulation internals are never scored. |
| **Rigging / skinning** (bones, weights, IK) | brainstorm, formats | 3D/4D | glTF native (`skins`, joints) | **outcome-checked only**: joint transforms at declared frames, within tolerance. The IK solve itself is not scored. |
| **Materials / appearance** (colour, texture, shading, lighting) | brainstorm | all | all six native | Not checkable as "correct". At most, a declared property can be compared for equality/difference. |
| **Text / typography** (glyph rendering, kerning, font fallback) | formats | 2D | SVG, PPTX, Lottie | Split verdict: the **bounding box is core** (it is a geometric primitive and is checked), but glyph rasterization and font fallback are not. |

## Out-of-scope concepts

| Concept | Why out |
|---|---|
| Rendering / image quality (pixel fidelity, AA, shading) | Explicit project scope: we validate **content**, not rendering. Recognized viewers render for human inspection only and are never scored. |
| Tool automation / live-editor macros | Explicit project scope: not tool automation. Adapters into real apps are M3, post-paper. |
| Cost / quantity takeoff (SINAPI line items, BOQ) | Consumes IFC-derived geometric quantities (volume/area — already core), but pricing is not a spatial or temporal predicate. |
| Audio, narrative, dialogue | Non-spatial content channel. |
| Gameplay / behaviour scripting | Application logic layered on geometry, not geometry. |
| Freehand / undeclared CV-ingested geometry | Belongs to the separate `perception/` CV→semantics bridge (itself flagged investigate/prune), not to the grammar. |
| Aesthetic judgement ("looks balanced", "pleasing layout") | Not deterministically checkable **by construction** — the exact thing the filter exists to exclude. |

## Why the last row matters

"Aesthetic quality" is the honest boundary of this project. A system that claimed to verify it would be
lying, and a checker that scored it would be gameable. Excluding it is what lets every remaining claim in
[INVENTORY.md](INVENTORY.md) be defended.
