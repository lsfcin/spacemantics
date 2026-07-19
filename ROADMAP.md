# Spacemantics — Roadmap
> Pending work only. Completed milestones are in [HISTORY.md](HISTORY.md).

## Status
**M0 · M0.5 · most of M1 complete** (see HISTORY.md). The thin kernel + checker are built and public
(github.com/lsfcin/spacemantics, 43 tests green); surface v2 regenerated; paper on Overleaf (ICLR, 10pp).
A **visual WITH/WITHOUT pilot** (`bench/` + `adapters/`) is built and demonstrated, but the real
comparison is blocked on an on-slate model. Next: **M2** — the actual C0→C3 numbers, which need a model.

## Backlog
- `cv-go-nogo`: which CV primitives survive (detection/segmentation 2D, depth 2.5D/3D, tracking 4D).
- `core-tools-wrapper`: add `core/tools/spatial-check` only if the checker is reused cross-project.

---

## Milestone 1 — remaining (mostly complete; see HISTORY.md for what shipped)

### W3b — prose parser (deferred)
The checker consumes the JSON AST directly and is fully exercised through it (43 tests + CLI). A
controlled-English **parser** (prose → AST) implementing `dsl/GRAMMAR-PROSE.ebnf` v2 is the remaining
surface work. Deferred: not on the M1 critical path because prose-vs-JSON is an M2 ablation axis, not a
checker dependency. The grammar it must implement is written and example-traced.

### Verification still owed (from the W3 charter)
- [ ] **cross-format consistency test** — one scene → SVG **and** glTF → parse back → identical checker
      verdict (the real test of the conventions reconciliation). SVG *emit* exists (`adapters/`); the
      SVG→scene **parser** and a glTF adapter do not yet.
- [ ] **dogfood parse** — one isoroll scene + one casinhas module as a 7× parametric array. Blocked on the
      spatial-array concept, currently demoted (see `dsl/CHECKABILITY.md`).

### The three design decisions (do not re-litigate)
1. **Verbs are sugar over `create` + `constrain`.** Actions = the ordered program; claims = the unordered
   spec, and the only thing scored. Buys editing without weakening verification (Gumin et al.: imperative
   beat declarative 82–94% for layout).
2. **Articles are a checked type system on identity.** `a`/`an` introduces (only with `add`/`create`);
   `the` refers. `move a ball` is a parse error, not a silent create. `the ball` legal iff exactly one exists.
3. **One canonical phrasing per concept — no synonyms.**

### Key Files (reference)
`academy/papers/spacemantics/outputs/texpace-foundations.md` §6 + the 5 research packs. isoroll:
`depthZIndex = (row − col + elev)·10000 + band` (`code/isoroll-module/src/render/iso-tile-depth.ts`);
tolerances IoU≥0.9, DIM_TOLERANCE=0.02, ALPHA_MIN=8 (`code/isoroll-content/src/cli/sheet_qc.py`); chirality
rule (rotation = cell remap, never mirror); six coord systems (`src/transform/coord-map.ts`). Slides:
`rotation_deg=atan2(shearY,scaleX)` (`core/tools/slides_style.py`). corpora: `Box3D`/`Pose6DOF` —
**ordinal-only**, never metric. casinhas: `build_ifc.py` + `mapeamento_ifc.csv` selector schema.

---

## Milestone 2 — benchmark execution + cross-model sweep 🔲 PENDING

### Problem
Produce the evidence: does texpace + checker lift LLM spatial capability, across dimensions and models?

### Unblock first — the pilot is built, the model is missing
The `bench/` harness (WITHOUT / blind / WITH arms, checker-scored) and the `adapters/` SVG render exist.
The pilot ran only on Gemini (off-slate, quota-limited). To get a real number:
- [ ] **Wire the real model slate** into `bench/model_client.py` — an Anthropic branch (Haiku 4.5,
      Sonnet 5, Opus 4.8, Fable 5) and an opencode branch (GLM 5.2, DeepSeek v4 Pro). Provider is data;
      one branch per transport. The moment a key exists, the WITHOUT/WITH run goes.
- [ ] **SVG → scene parser** (round-trip) — needed to *score* a model's raw-SVG output in the WITHOUT arm.
      `adapters/` only *emits* today.
- [ ] **3D / isometric render** in `adapters/` — currently 2D top-down footprints only.

### Then the full design
- Build the 13 task families × 3 levels from `tasks/TAXONOMY.md`; ground truth machine-checkable.
- Conditions C0 (free-text/JSON) → C1 (+DSL) → C2 (+skill guards) → C3 (+checker feedback loop, bounded k).
  Per M0.5: the model **reasons in free text, then emits** — never decode reasoning under a rigid schema.
- **Surface ablation:** run C1–C3 in both prose and JSON (the surface is a free variable). If prose ≈ JSON
  we replicate the "surface doesn't matter" finding; if they diverge, our framing is wrong.
- Full model sweep across the slate above.
- `perception/` — CV go/no-go per primitive (reuse `code/corpora/`, ordinal-only today).

### Checklist
- [ ] task generators + ground truth for the 13 families
- [ ] C0–C3 conditions + bounded feedback loop
- [ ] full cross-model results tables + ablation (attribute the lift: DSL vs guards vs checker)
- [ ] `perception/` CV go/no-go decisions
- [ ] hand results to the paper (results + discussion)

**Pilot finding to carry forward:** at generous tolerance on simple scenes a strong model needs no checker
(no headroom); the lift, if any, appears on hard/dense scenes where the baseline breaks. Design the
families so most sit in that regime, or report per-difficulty.

---

## Milestone 3 — transfer: real app adapters + dogfood 🔲 PENDING

### Problem
Turn the capability into everyday leverage — and make the stronger claim: *the grammar survives contact
with tools it was not designed against.*

### Solution
Adapters from the open formats into real applications:
- **isoroll / Foundry** — texpace → Tiled TMX / scene manifest → `src/assemble/`; adopt the canonical depth
  convention, retire the three conflicting ones; wake the dormant `DepthSorter`.
- **casinhas** — texpace → IFC via `modelo/build_ifc.py` (7× parametric array + per-instance overrides).
- **Blender / Bonsai** — glTF + IFC round-trip; the physics-execution engine for outcome-checked tasks.
- **Remotion** — Lottie → video (Remotion enters only here).
- Slides/animation skill for teaching material (PPTX + Lottie).
Post-paper. Each adapter declares its conformance level + conventions.
