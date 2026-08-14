# Spacemantics — Roadmap
> Pending work only. Done work is deleted; git is the history.

## Status
**M0 · M0.5 · most of M1 complete.** The thin kernel + checker are built and public
(github.com/lsfcin/spacemantics, 43 tests green); surface v2 regenerated; paper on Overleaf (ICLR, 10pp).
A **visual WITH/WITHOUT pilot** (`bench/` + `adapters/`) is built and demonstrated, but the real
comparison is blocked on an on-slate model. Next: **M2** — the actual C0→C3 numbers, which need a model.

## Backlog
- `cv-go-nogo`: which CV primitives survive (detection/segmentation 2D, depth 2.5D/3D, tracking 4D).
- `core-tools-wrapper`: add `core/tools/spatial-check` only if the checker is reused cross-project.
- `texpace-as-tool-layer`: **hypothesis from Lucas (INBOX 2026-08-14), flagged by him as needing a
  check before it is believed** — *"texpace deve ser acoplado às ferramentas (tools), uma camada
  entre agentes e tools, agentes não poderiam usar CLI diretamente, tudo seria via texpace"*, i.e.
  one interface that translates word-semantics into spatial/geometric actions **and blocks commands
  that are possible but wrong**. The blocking half is the interesting half and it is genuinely this
  project's thesis — the checker owning geometric truth is exactly "possible but wrong, refused".
  **The tension to resolve first:** [CONTEXT.md](CONTEXT.md) declares scope as validating *content*
  in open formats, explicitly **not tool automation**. So this either (a) widens M3's transfer scope
  deliberately, or (b) is really the narrower `core-tools-wrapper` above wearing an ambitious
  framing. Decide which before designing anything; they differ by an order of magnitude in cost.
  Note also that a mandatory layer over *every* CLI would be a hard gate on tools that have nothing
  spatial about them (`gmail`, `papers`, `web/search`), which is an argument for scoping it to the
  tools that emit or consume geometry.

---

## Milestone 1 — remaining

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

### Unblock first — model slate + SVG scoring done; one lane still owed
The `bench/` harness (SVG / WITHOUT / blind / WITH arms, checker-scored), the real model slate
(`claude-cli` + `opencode` transports), and the SVG round-trip all exist and ran for real.
Remaining:
- [ ] **Re-run the opencode lane** (GLM 5.2, DeepSeek v4 flash) on `tasks_2d.json` with the hardened
      transport (`bench/cli_transport.py`, `plan` agent + retry, commit 458e8a9). It died silently
      mid-run in the background-task environment last session — cause not diagnosed (no error, no
      partial output); prefer running it in the foreground / watched rather than backgrounded. A
      **pre-hardening** run showed real WITH-blind lift on both (GLM +15.0pp, DeepSeek +11.7pp) but
      is not trustworthy (ran under the agentic-write bug) — do not cite those numbers, re-run instead.
- [ ] **`tasks_2d.json` is saturated for the Anthropic slate** (Haiku + Sonnet both solve it ~100% in
      every arm, no lift). Either it's the wrong instrument for strong models (need a harder tier) or
      weaker models (GLM/DeepSeek) are where this suite's signal actually lives — the re-run above
      will tell us which. Don't add "make it harder" work until that's known.
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
