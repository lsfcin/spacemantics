# Spacemantics — Roadmap
> Pending work only. Completed milestones move to HISTORY.md.

## Status
M0 scaffold + M0.5 foundations research done (2026-07-12). DSL named **texpace**; v0 design principles
distilled in `academy/papers/spacemantics/outputs/texpace-foundations.md` §6. Next: **M1** — 2.5D
vertical slice (write grammar v0 + checker, first C0→C3 lift numbers).

## Backlog
- `cv-go-nogo`: which CV primitives survive (detection/segmentation 2D, depth 2.5D/3D, tracking 4D).
- `core-tools-wrapper`: add `core/tools/spatial-check` only if the checker is reused cross-project.

---

## Milestone 0.5 — texpace foundations (research before build) ✅ COMPLETE

### Problem
Before writing grammar v0, validate that a prepose-like verifiable spatial DSL has real potential for
LLMs, and map the full design space so texpace is grounded in prior art, not invented blind. texpace
must handle spatial AND temporal relations among *any* content, under multiple anchor coordinate
systems (world / group / locale), covering proximity, alignment/vector relations, and directional
relations relative to a chosen frame.

### Solution
Delegated deep research (deepresearch flow / sub-agents) producing
`academy/papers/spacemantics/outputs/texpace-foundations.md`. Sub-questions:
1. **Frames of reference** — Levinson intrinsic/relative/absolute → maps to texpace world/group/locale
   anchors; how the anchor selects which directional relations are valid.
2. **Qualitative spatio-temporal calculi** — RCC-8 (topology), Cardinal Direction Calculus / Rectangle
   Algebra (direction), Allen's interval algebra (time), STCC (combined) — what texpace should borrow
   as its relation set + consistency checking.
3. **Spatial-language lexicon map** — enumerate the language carrying spatial meaning (prepositions,
   projective terms, proximity, alignment, containment, contact, orientation) + temporal connectors
   (before/after/during/then, repeat, maintain). Ground with computational models (Regier & Carlson
   AVS for projective terms). Seed from the corpora slides (verbs + connectors + dynamics + modifiers).
4. **Prior DSLs / verification** — SpatialGrammar, HDSL, PSDL, declarative-vs-imperative scene programs,
   Cassowary constraint solving, USD/SDF/glTF scene description; and prepose's Z3 verification pattern —
   what to reuse for texpace's checker.
5. **Potential verdict** — does DSL-as-IR + verification measurably help LLMs (evidence for/against),
   and where it breaks.

### Checklist
- [x] run deepresearch on the five sub-questions (5 researcher subagents Q1-Q5)
- [x] write `academy/papers/spacemantics/outputs/texpace-foundations.md` (+ provenance; verdict + 28 verified refs)
- [x] distill into texpace v0 design principles (relation set, anchor model, temporal ops) → foundations doc §6

### References
Seed captures in `academy/papers/spacemantics/outputs/research-brief.md`. Corpora slides (atomic-verb +
connector + modifier grammar) as inspiration. Anchor analogy: Prepose (gesture DSL + Z3).

---

## Milestone 1 — texpace grammar v1 + benchmark design + first paper sections 🔲 PENDING

### Problem
The grammar is the key artifact and must be *designed*, not rushed. The v0 core is too thin for our own
scenarios (no spatial array — yet casinhas is 7 repeated modules; no units, tolerances, negation/
quantification, underspecification, conventions model). Worse, **our own backends contradict each other**
— see [CONFLICTS.md](dsl/CONFLICTS.md): 4-5 incompatible frames, 6 incommensurable units, 4 time bases,
4 rotation representations, 3 unshared repetition mechanisms. isoroll alone carries three conflicting
depth conventions. Naming one canonical convention fixes real bugs.

**Scope delimited:** texpace is validated on **content creation / editing / understanding** expressed in
**open standard model files** — not on rendering, not on tool automation. The checker parses the model
content; recognized viewers render for human inspection only and are never scored.

### Solution — five workstreams
- **W1 Inventory** (`dsl/INVENTORY.md`, `dsl/CONFLICTS.md`) — derive concepts from four sources (M0.5
  foundations · user brainstorm · our app inventory · the target formats' own data models). One row per
  concept × {source, dimensions, formats, deterministically checkable?, core|module|advisory|out}. Plus
  the conflict table with texpace's canonical choice + per-format mapping.
- **W2 Spec** (`dsl/SPEC.md`, `dsl/GRAMMAR.ebnf`, `dsl/CONFORMANCE.md`) — layered: **Kernel** (entities+
  identity+semantic type; anchors {world,locale,group} + **arity gate**; units & tolerances; DIR/DIST/
  TOP/PATH; time with explicit **time-base tag**; assertions-vs-constraints; negation & quantification;
  underspecification) · **Modules** (camera/projection · layers & z-order · hierarchy · parametric/arrays
  · timeline · appearance* · physics & rigging*) · **Profiles** (2D/2.5D/3D/4D) · **Adapters** (format
  emitters/parsers declaring conformance + conventions). *= advisory.
- **W3 Thin kernel + checker** (`dsl/`, `checker/`) — texpace → scene IR → emit ≥2 formats (SVG + glTF) →
  parse back → check. Checker = numeric grounding of definite scenes (RCC-8 topology, Rectangle-Algebra
  direction, Allen temporal, numeric distance/orientation), O(n²), explicit tolerances. **Enforces the
  checkability filter**: any `core` concept without a working predicate is demoted to advisory.
- **W4 Benchmark taxonomy** (`tasks/TAXONOMY.md`, design only) — 13 families × 3 levels (L1 naïve/sanity ·
  L2 common · L3 challenge), each anchored to literature. Family 7 (3D generic, glTF) = credibility anchor
  (head-to-head vs SceneCraft/SpatialGrammar/HDSL on their metrics); family 1 (planar-graph drawing) =
  calibration against published numbers.
- **W5 Paper sections** → `academy/papers/spacemantics/sections/{02_background,03_related_work,04_method}.tex`.

### Governing principle
**Strict checkability filter:** a concept that cannot be deterministically checked is NOT core — it goes
to the execution/advisory layer. Physics is **outcome-checked** (state initial conditions + goal
post-conditions; a recognized engine simulates; the checker verifies only observables — rest positions,
contact events, Allen event ordering — within tolerance).

### Format slate (open standards; the checker parses these)
SVG (2D vector/diagram/UI, 2.5D technical) · PPTX/OOXML (slides — chosen over ODP: equal ISO standing,
better round-trip fidelity + mature `python-pptx`) · Tiled TMX/TMJ (2.5D gaming — iso orientation, layers,
z-order native) · glTF 2.0 (3D generic; **animation + skinning/rigging** for 3D+time) · IFC ISO 16739
(BIM) · **Lottie** (2D+time — formal open standard: Linux Foundation, JSON schema, IANA `video/lottie+json`;
SVG SMIL is deprecated and NOT used).

### Checklist
- [x] W1 `dsl/INVENTORY.md` + `dsl/INVENTORY-ADVISORY.md` + `dsl/CONFLICTS.md`
- [x] W2 `dsl/SPEC.md` + `dsl/CONFORMANCE.md`
- [x] W4 `tasks/TAXONOMY.md` + `TAXONOMY-FAMILIES.md` — 13 families × 3 levels, literature-anchored
- [x] W5 paper sections 02/03/04 + `lib/refs.bib` — **compiles, 13pp, 0 undefined citations**
- [~] **W2b — surface v2 regeneration** (design decided 2026-07-12; see below) — TYPES.md done;
      SPEC three-line-kinds + articles done; EXAMPLES/GRAMMAR-PROSE/GRAMMAR-JSON/04_method still v1
- [x] **W3 thin kernel + checker** — `checker/` scores TOP·DIR·DIST·faces·align·quant·count·HOLD·Allen on
      definite scenes, O(n²); 39 tests green; CLI runs (`python -m checker examples/office.json`)
- [x] **W3c concepts × {checkable? how?} table** — `dsl/CHECKABILITY.md`; filter enforced, **4 core
      concepts demoted** (PATH-shape, nested transforms, spatial arrays, constraint-solving)

### W2b — surface v2 (DESIGN LOCKED, execution pending)

The function-call surface was rejected: it was the IR with parentheses. Redesigned as **controlled
English**. [LEXICON.md](dsl/LEXICON.md) is rewritten (v2) and is the contract. Remaining work is
mechanical — regenerate the dependents from it:

- [ ] `dsl/TYPES.md` — **new**. The type ontology carrying the **intrinsic-front flag** (`desk`, `chair`,
      `door`, `car`, `person` → has a front; `ball`, `panel`, `sphere` → does not). This flag gates
      `in front of` (locale vs group anchor), so it is load-bearing, not cosmetic. User-extensible:
      *"a lectern is a kind of furniture with a front."*
- [x] `dsl/TYPES.md` — type ontology + intrinsic-front flag; mirrored in `checker/types.py`.
- [x] `dsl/EXAMPLES.md` — all six examples rewritten in v2 prose (verbs + articles + setup/action/claim).
      Fixed a v1 semantic bug: `left of the desk` is legal (desk has a front); the error case needs a
      frontless ground (`left of the ball`), matching `checker/test_direction.py`.
- [x] `dsl/GRAMMAR-PROSE.ebnf` — regenerated from LEXICON v2; article rule is now syntactic (`move a ball`
      is a grammar error); per-example parse trace + semantic side conditions documented.
- [x] `dsl/GRAMMAR-JSON.md` — regenerated against the **real** checker AST (`loader.py`/`evaluate.py`),
      not an invented schema; bijection table maps the six examples; `examples/office.json` is a live instance.
- [x] `dsl/SPEC.md` — three-line-kinds model (setup / action / claim) + articles-as-identity-type added.
- [x] `sections/04_method.tex` — dual-surface paragraph + surface ablation (C1–C3 in both surfaces); paper
      recompiles (10pp, 0 undefined citations).

### W3b — prose parser (deferred)
The checker consumes the JSON AST directly and is fully exercised through it (39 tests + CLI). A
controlled-English **parser** (prose → AST) implementing GRAMMAR-PROSE.ebnf v2 is the remaining surface
work. Deferred: not on the M1 critical path because prose-vs-JSON is an M2 ablation axis, not a checker
dependency. The grammar it must implement is now written and example-traced.

**The three design decisions (do not re-litigate):**
1. **Verbs are sugar over `create` + `constrain`.** Actions = the program (ordered); claims = the spec
   (unordered, and the only thing the checker scores). This buys editing — inherently imperative, and
   half the project's scope — without weakening verification. Backed by Gumin et al. (imperative beat
   declarative 82–94% forced-choice for layout).
2. **Articles are a checked type system on identity.** `a`/`an` introduces (legal only with `add`/
   `create`); `the` refers (required by `move`/`delete`/`rotate` and all claims). `move a ball` is a
   **parse error**, not a silent create — silent creation forks the scene invisibly and surfaces the
   error far away. Plus the uniqueness rule: `the ball` is legal only if exactly one ball exists.
3. **One canonical phrasing per concept — no synonyms.** Every alias is another near-miss a model can
   emit and another parser branch.

### Verification
Filter enforced (every `core` concept has a predicate + tolerance, else demoted) · **cross-format
consistency test** (one scene → SVG and glTF → parse back → identical checker verdict; the real test of
the conventions reconciliation) · each of the 5 conflicts has a canonical choice + per-format mapping +
a unit test · **dogfood parse** (one isoroll scene + one casinhas module as a 7× parametric array) ·
`latexmk` compiles and every claim traces to a `refs/*.yaml`.

### Key Files
Reuse `academy/papers/spacemantics/outputs/texpace-foundations.md` §6 + the 5 research packs. isoroll
canonical values: `depthZIndex = (row − col + elev) * DEPTH_SCALE + band` (DEPTH_SCALE=10000,
TOKEN_BAND=5000, `code/isoroll-module/src/render/iso-tile-depth.ts`); tolerances IoU≥0.9,
DIM_TOLERANCE=0.02, ALPHA_MIN=8 (`code/isoroll-content/src/cli/sheet_qc.py` — the *content* repo, not the
module); facing `N..NW+TOP`; **chirality rule** (rotation = cell remapping, never
mirroring); six coord systems (`src/transform/coord-map.ts`). Slides: `compose_transforms`,
`rotation_deg=atan2(shearY,scaleX)` (`core/tools/slides_style.py`). corpora: `Box3D`/`Pose6DOF` —
**ordinal-only** (relative depth, hardcoded focal length); never type it as metric. casinhas:
`build_ifc.py` params + `mapeamento_ifc.csv` type-level selector schema.

### Scope
Design + thin validation only. Benchmark execution and cross-model runs = M2.

---

## Milestone 2 — benchmark execution + cross-model sweep 🔲 PENDING

### Problem
Produce the evidence: does texpace + checker lift LLM spatial capability, across dimensions and models?

### Solution
- Build the 13 task families × 3 levels from `tasks/TAXONOMY.md`; ground truth is machine-checkable.
- Conditions C0 (free-text/JSON) → C1 (+DSL) → C2 (+skill guards) → C3 (+checker feedback loop, bounded k).
  Per M0.5: the model must **reason in free text, then emit the DSL** — never decode reasoning under a
  rigid schema (format restriction measurably degrades reasoning).
- **Surface ablation (tests our own thesis).** texpace has two bijective surfaces — controlled-English
  *prose* and *JSON* — over one AST, so the surface is a free experimental variable. Run C1–C3 in both.
  Our claim is that the checker, not the notation, carries the lift; GeoGramBench found drawing-language
  choice worth <1%. If prose ≈ JSON we replicate that cross-domain (a result). If they diverge, our
  framing is wrong (a more important result). Either way we measure instead of guessing.
- Full model sweep: Haiku 4.5, Sonnet 5, Opus 4.8, Fable 5 (API); GLM 5.2, DeepSeek v4 Pro (opencode).
- `perception/` — CV go/no-go per primitive (reuse `code/corpora/`). Drop any primitive whose own error
  swamps the model-lift signal. Remember corpora is **ordinal-only** today.

### Checklist
- [ ] task generators + ground truth for the 13 families
- [ ] C0–C3 conditions + bounded feedback loop
- [ ] full cross-model results tables + ablation (attribute the lift: DSL vs guards vs checker)
- [ ] `perception/` CV go/no-go decisions
- [ ] hand results to the paper (results + discussion)

---

## Milestone 3 — transfer: real app adapters + dogfood 🔲 PENDING

### Problem
Turn the capability into everyday leverage — and make the stronger research claim: *the grammar survives
contact with tools it was not designed against.*

### Solution
Adapters from the open formats into real applications (the M1/M2 work targets formats, not apps):
- **isoroll / Foundry** — texpace → Tiled TMX / scene manifest → `src/assemble/`; adopt the canonical
  depth convention and retire the three conflicting ones; wake the dormant `DepthSorter`.
- **casinhas** — texpace → IFC via `modelo/build_ifc.py` (7× parametric array + per-instance overrides).
- **Blender / Bonsai** — glTF + IFC round-trip; the physics-execution engine for outcome-checked tasks.
- **Remotion** — Lottie → video (this is where Remotion finally enters; it is out of scope until here).
- Slides/animation skill for teaching material (PPTX + Lottie).
Post-paper. Each adapter declares its conformance level + conventions.
