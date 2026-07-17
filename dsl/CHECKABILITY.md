# texpace — Checkability Filter (enforced)
> Every INVENTORY concept × {has a working predicate? which one?}. Concepts without one are demoted here, not in a claim table.

This file is the **output of running the filter**, not a restatement of the intent. The rule (CONTEXT.md
line 13): *a concept that cannot be deterministically checked does not enter the kernel.* Until a predicate
executes, "every `core` concept has a predicate" is a claim in [INVENTORY.md](INVENTORY.md). Here it is a
fact traced to code in [`../checker/`](../checker/CONTEXT.md), with the demotions the run forced.

**Status key.** `KERNEL` = a working predicate scores it, with a passing test. `MODULE` = checkable in
principle, predicate deferred (named, not built). `DEMOTED` = INVENTORY called it `core`; no predicate
exists in the thin kernel, so it drops to module/advisory until one does. `ADVISORY` = executed, never
scored (by design).

## Core concepts — the filter run

| Concept (INVENTORY) | Predicate in `checker/` | Test | Status |
|---|---|---|---|
| `TOP(a,b,rcc)` | `rcc8.relation` — all 8 codes on definite regions, O(1)/pair | `test_topology.py` (7) | **KERNEL** |
| `DIR(fig,gnd,axis,anchor)` | `direction.holds` — Rectangle Algebra (Allen per axis) in canonical frame | `test_direction.py` (8) | **KERNEL** |
| `DIST(fig,gnd,θ)` | `metrics.distance_holds` — point-to-region vs unit-tagged threshold | `test_metrics.py` | **KERNEL** |
| Anchor `{world,locale,group}` + arity gate | `direction.axis_for` — refuses an unreadable projective term as ERROR, not FAIL | `test_direction.py` | **KERNEL** |
| Entity semantic type / intrinsic-front flag | `types.Ontology.has_front` — inherited through the lattice | `test_direction.py`, `test_declarations.py` | **KERNEL** |
| Units & scale (unit-tagged quantity) | `units.Quantity.to_metres` — 5 unit kinds → metres | `test_metrics.py` | **KERNEL** |
| **The ordinal rule** (rank ≠ magnitude) | `units.to_metres` raises `UnitTypeError` for `ordinal` in a metric predicate | `test_metrics.py::…type_error` | **KERNEL** |
| Tolerance / epsilon | `scene.Tolerance` — mandatory; every predicate compares `\|Δ\|<ε` | `test_declarations.py` | **KERNEL** |
| Frame declaration (handedness/up/origin) | `loader._require_frame` — non-canonical frame rejected at the door (C1) | `test_declarations.py` | **KERNEL** |
| Negation & quantification (∀/∃) | `evaluate._quantified` — `none`/`every` over the O(n²) pair matrix, with witness | `test_quantifiers.py` | **KERNEL** |
| Coverage (`count`) | `evaluate._count` — stops the "solve by deleting objects" exploit | `test_quantifiers.py` | **KERNEL** |
| Underspecification (free DOFs) | `evaluate._free_dofs` — reported as SKIPPED, never scored | `test_declarations.py` | **KERNEL** |
| Orientation/rotation (unit quaternion) | `vecmath.rotate/basis_of` — no Euler, ever (C4) | via DIR/FACES tests | **KERNEL** |
| Alignment / parallel / perpendicular / faces | `metrics.faces`, `metrics.axis_angle_holds`, `metrics.aligned` | `test_metrics.py` | **KERNEL** |
| Schematization (figure→point, ground→region) | `geometry.point_to_region_distance` | `test_metrics.py` | **KERNEL** |
| Temporal `AT(t)` / `OVER(interval)` | keyframe interp + `HOLD` sampled invariant | `test_temporal.py` | **KERNEL** |
| Composition `SEQ`/`PAR` (ordering) | `allen.relation` over declared event intervals | `test_temporal.py::…allen` | **KERNEL** |
| Assertion vs constraint | `report.Verdict.mode` — assertion scored; **constraint recorded, not solved** | — | **KERNEL (assert) / DEFERRED (solve)** |
| Selectors / identity | `scene.select` — by type and by name; **indexed `houses[3]` needs arrays** | `test_quantifiers.py` | **KERNEL (partial)** |
| Geometric primitives | `geometry` — box / sphere / point → AABB; **curves/polylines/meshes not built** | `test_topology.py` | **KERNEL (partial)** |

## Demotions the run forced

These INVENTORY rows are tagged `core` but **have no working predicate in the thin kernel**. The filter
demotes them. Each names what would restore it — the honest backlog, not a silent gap.

| Concept | Why it fell out | Where it goes | Restored by |
|---|---|---|---|
| `PATH(fig,gnd,traj,τ)` **shape** — `passes behind/over/through`, `enters/leaves` as a *dedicated* predicate | Only the **sampled** reading is built: `HOLD`/`AT` + per-instant `TOP`/`DIR` over interpolated poses. The trajectory-*shape* constraint (the "behind" arc, the through-line) has no predicate. `enters` = `PATH ⇒ finally NTPP` is checkable by two `AT` endpoints today, but not as one PATH predicate. | **MODULE** `timeline` | a trajectory-error predicate over sampled waypoints + a shape term |
| Coordinate systems / **nested transforms** | The kernel stores absolute pose per entity. No `child_world = parent_world ∘ local` composition exists. | **MODULE** `hierarchy` | transform-chain composition + a cycle check |
| Parametric variables + **spatial arrays** w/ overrides | `loader` does no array expansion; `casa ×7` cannot be written or checked. This is the casinhas dogfood — currently unreachable. | **MODULE** `parametric` | expand-then-check in the loader; then indexed selectors resolve |
| Constraint **solving** (goal-to-satisfy) | Constraints are recorded and reported, never solved; only assertions are scored. Foundations §4's tiered solver (Cassowary → QC → Z3) is unbuilt. | **DEFERRED** (M2) | a solver behind the `constrain` mode; the assertion path already scores generated scenes |

## What this buys the paper

The sentence "every core concept carries a checkable predicate" is now **false as originally written, and
we can say exactly where** — four demotions, each with a named restoration. That is a stronger claim than
an unfalsified table: the filter *did* something. The kernel scores 15+ concepts with passing tests
(`pytest tests` green, 39 cases); four `core` concepts were demoted for lack of a predicate; the demotions
are the M1→M2 boundary, not hand-waving.

**Method note for §04.** The checker runs on **definite scenes by numeric grounding** — O(n²) over
pairwise predicates, no NP-hard constraint network touched. Consistency-checking over indefinite networks
(RCC-8 tractable fragments, Allen ORD-Horn) is explicitly out of the thin kernel and unneeded for scoring
a concrete scene.
