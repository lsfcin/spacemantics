# Spacemantics
> Verifiable spatial DSL (texpace) + deterministic checker that lift LLM spatial capability across 2D/2.5D/3D/4D
> goal: [spacemantics](../../brain/goals/spacemantics.md)

**Thesis.** LLMs are weak at spatial tasks because they lack the right *interface*, not the capability.
This project supplies that interface: **texpace**, a spatial+temporal DSL; a **checker** that owns
geometric truth (the model's eyes never assert geometry); and a **benchmark** measuring the lift across
dimensions and models.

**Scope.** We validate **content** — model files in open standards (SVG, PPTX, Tiled TMX, glTF, IFC,
Lottie) — *not* rendering and *not* tool automation. Recognized viewers render for human inspection only;
they are never scored.

**Governing principle.** The lift comes from the **checker**, not the grammar surface. Hence the
*checkability filter*: a concept that cannot be deterministically checked does not enter the kernel.

## Start here

| I want to… | Go to |
|---|---|
| Understand the language | [`dsl/`](dsl/CONTEXT.md) — its CONTEXT gives the reading order |
| Know what's planned / in flight | [ROADMAP.md](ROADMAP.md) — M1 design · M2 benchmark · M3 transfer |
| See the benchmark design | [`tasks/`](tasks/CONTEXT.md) — 13 families × 3 levels |
| Know *why* any of this is true | `academy/papers/spacemantics/outputs/texpace-foundations.md` |
| The human-facing hub | `brain/goals/spacemantics.md` |

## Module map

| Module | State | Purpose |
|---|---|---|
| [`dsl/`](dsl/CONTEXT.md) | **designed** (M1) | texpace: inventory, conventions, spec, grammar, conformance |
| [`tasks/`](tasks/CONTEXT.md) | **designed** (M1) | benchmark taxonomy — 13 families × 3 levels, literature-anchored |
| `checker/` | planned (M1 W3) | deterministic verifier: RCC-8 topology · Rectangle-Algebra direction · Allen temporal · numeric distance/orientation. Definite scenes only → O(n²) |
| `adapters/` | planned (M2) | format emitters/parsers (SVG, PPTX, TMX, glTF, IFC, Lottie); each declares conformance + conventions |
| `bench/` | planned (M2) | harness + provider-agnostic cross-model runner; conditions C0–C3 |
| `perception/` | investigate/prune (M2) | CV visuals→semantics bridge. `code/corpora` depth is **ordinal-only** — it can never satisfy a metric predicate |

Paper twin: `academy/papers/spacemantics/`. Coordinating goal: `brain/goals/spacemantics.md`.

<!-- routing:start -->
## Routing

| Subdirectory | Description |
|--------------|-------------|
| [`adapters/`](adapters/CONTEXT.md) | Render a texpace scene to a viewable open format. SVG first — 2D, needs no engin |
| [`bench/`](bench/CONTEXT.md) | The WITH/WITHOUT pilot: does the checker-in-the-loop lift a model's spatial plac |
| [`checker/`](checker/CONTEXT.md) | Deterministic verifier: it owns geometric truth so a model's eyes never assert g |
| [`dsl/`](dsl/CONTEXT.md) | The texpace language: concept inventory, conventions reconciliation, spec, gramm |
| [`tasks/`](tasks/CONTEXT.md) | Benchmark scenario taxonomy: 13 open-format families × 3 difficulty levels, mach |
| [`tests/`](tests/CONTEXT.md) | — |

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`HISTORY.md`](HISTORY.md) | — | — | History |
| [`README.md`](README.md) | — | — | Spacemantics |
| [`ROADMAP.md`](ROADMAP.md) | — | — | Spacemantics — Roadmap |
<!-- routing:end -->
