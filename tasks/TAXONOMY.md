# texpace — Benchmark Scenario Taxonomy
> 13 task families × 3 difficulty levels; toy/synthetic, machine-checkable, content-only (never rendering-scored)

Companion: [TAXONOMY-FAMILIES.md](TAXONOMY-FAMILIES.md) — per-family task specs with a concrete L1/L2/L3
example for each of the 13 families.

## 1. Principles

- Tasks are **toy/synthetic**: a natural-language spec plus an unambiguous ground-truth scene, small enough
  to reason about by hand.
- **Machine-checkable, not rendering-checked.** The checker (`checker/`, per `dsl/SPEC.md`) parses open
  standard model file **content** — SVG/PPTX/TMX/glTF/IFC/Lottie — never a rasterized image. Recognized
  viewers exist for human inspection only and are never scored (ROADMAP.md M1 scope).
- **Ground truth is generated, not hand-authored.** A parametric generator emits the scene from a seed +
  difficulty knobs, so (a) difficulty is a controllable dial, not editorial judgment, and (b) any reviewer
  can regenerate the identical scene from the seed and reproduce a scored run.
- Each task = `{ spec: natural language, seed: generator input, ground_truth: texpace scene, format:
  emitted file }`. The model never sees `ground_truth` or `seed`; only the checker does.

## 2. The three levels (applied uniformly across all 13 families)

| Level | Name | Definition |
|---|---|---|
| **L1** | naive / sanity | Setup + smoke. Few objects (≤~4). `world` anchor only. Unambiguous relations. No negation, no quantification. Proves the pipeline runs end-to-end (generate → model → parse → check). |
| **L2** | common | Realistic composition. Mixed anchors (`world`+`locale`, occasionally `group` with a bound viewpoint). Moderate relation depth (chains of 2-3 relations). Some quantification (`exactly N`, `at least N`). |
| **L3** | challenge | Adversarial. Viewpoint-relative (`group`) reasoning with an explicit `viewpoint_transform`. Occlusion/depth cycles. Negation (`no two X overlap`) and quantification (`every X faces Y`, count coverage). Parametric repetition (arrays with per-instance overrides). Tight tolerances. |

Level is a property of the **spec + ground truth**, not of the format — the same family's generator
produces all three levels from the same generator with different difficulty knobs.

## 3. The 13 families

| # | Family | Format | Anchors to |
|---|---|---|---|
| 1 | 2D graph/diagram drawing | SVG | PlanarBench, GeoGramBench (**calibration** — numbers comparable to published results) |
| 2 | 2D vector diagram | SVG | SVGenius, GeoSVG-RL |
| 3 | 2D UI layout | SVG | LLMs-as-Layout-Designers, Cassowary constraints |
| 4 | 2D slides | PPTX | content-aware layout literature |
| 5 | 2.5D technical/engineering | SVG + declared iso projection | novel |
| 6 | 2.5D gaming | Tiled TMX | novel — depth/occlusion, isoroll dogfood |
| 7 | 3D generic modeling | glTF | SceneCraft / SpatialGrammar / HDSL (**credibility anchor** — head-to-head on their own metrics) |
| 8 | 3D IFC/BIM | IFC | novel — parametric repetition, storeys, quantities |
| 9 | 2D + time, kinematic | Lottie | PRISM |
| 10 | 2D + time, physics (outcome-checked) | Lottie + engine | PRISM + novel |
| 11 | 3D + time incl. rigging | glTF animation | novel |
| 12 | Cross-view / multi-viewpoint consistency | glTF / SVG | COMFORT (**arity gate**) |
| 13 | Convention reconciliation / dogfood | cross-format | novel — isoroll's three depth conventions |

Per-family detail (open format rationale, spatial concepts exercised, literature anchor, and one concrete
task per level) is in [TAXONOMY-FAMILIES.md](TAXONOMY-FAMILIES.md).

## 4. Conditions (C0 → C3)

Per `academy/papers/spacemantics/outputs/texpace-foundations.md` §5 and ROADMAP M2:

| Condition | What's added | Rule |
|---|---|---|
| **C0** | free-text / JSON scene description | baseline; no DSL, no checker |
| **C1** | +texpace DSL | model emits texpace instead of free JSON |
| **C2** | +skill guards | grammar-constrained decoding / authoring guardrails around C1 |
| **C3** | +checker feedback loop | bounded **k rounds**; checker verdict fed back, model revises |

**Critical design rule** (foundations §5.2, non-negotiable): the model must **reason in free text, then
emit the DSL** — never decode its reasoning under a rigid schema. Format restriction measurably degrades
reasoning; this applies at every condition C1-C3, including inside the C3 feedback loop.

## 5. Metrics

Per-relation and per-task, computed by the checker (never a VLM or human):

- **Per-relation satisfaction** — fraction of DIR/DIST/TOP/PATH assertions the checker verifies true.
- **Coordinate / anchor error** — numeric deviation on `world`/`locale`/`group` positions; anchor-gate
  violations (e.g. `group` without a bound viewpoint) score as hard failures, not partial credit.
- **z-order accuracy** — painter's-algorithm / occlusion correctness (families 6, 12, 13).
- **Cross-view consistency** — the same `group` statement evaluated under multiple viewpoints yields
  transform-consistent verdicts (family 12; the arity-gate exercise).
- **IoU** — bounding/region overlap where applicable (2D/2.5D families).
- **Task success** — all-relations-satisfied, binary, per task.
- **4D-only**: temporal-order accuracy (Allen relations) + trajectory error (families 9-11).

Report **lift C0→C3**, disaggregated per family × level × model (ROADMAP M2 checklist item).

## 6. Threats to validity

- **Evidence asymmetry.** Every strong published DSL+checker result (SpatialGrammar, SceneCraft, HDSL) is
  **3D-indoor**. Our 2D (families 1-4), 2.5D (5-6), and 4D (9-11) columns have no comparable prior
  numbers — that is simultaneously texpace's novelty claim and its greatest exposure: there is no one to
  calibrate against there.
- **Verifier gaming.** A checker that only scores positive relations can be satisfied by a degenerate
  scene (HDSL's rewrite baseline silently deleted objects while passing its geometric checks). L3's
  negation (`no two overlap`) and coverage (`every X faces Y`, count constraints) exist specifically to
  close this hole — the same "make the bug a parse/check error" strategy as `dsl/CONFLICTS.md`.
- **Ceiling effect.** The loop closes the *spec-satisfaction gap*, capped by the model's intrinsic spatial
  reasoning ceiling (GeoGramBench: fine-tuning gains plateau at +3pp). A high C3 lift number cannot be
  read as "spatial cognition solved."
- **Loop cost.** The C3 feedback loop is bounded (k rounds) precisely because prior art's loops are
  expensive (HDSL ≈383s/scene) and gains flatten quickly — cost/latency is a reported dimension, not an
  afterthought.
