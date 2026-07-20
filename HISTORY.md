# History

Archive of completed work and resolved issues.

## Completed — 2026-07-20

### M2 unblock — real model slate + raw-SVG scoring
`bench/model_client.py` gained two local-CLI transports (`bench/cli_transport.py`): `claude-cli`
(subscription `claude -p`; haiku/sonnet/opus/fable) and `opencode` (`opencode run`; working ids
`nvidia/z-ai/glm-5.2`, `nvidia/deepseek-ai/deepseek-v4-flash` — `deepseek-v4-pro` times out, Alibaba
token expired, ollama-cloud needs a subscription). No API key needed; unblocks M2 without waiting on one.

`adapters/svg_parse.py` closes the SVG round-trip: emitter output inverts exactly (new `id` + `data-*`
frame metadata on the SVG root), model-emitted SVG reads under a metre contract (1 unit = 1 m, y
flipped). New raw-SVG arm in `bench/arms.py` (2D suites only), anchor-aligned before scoring
(`scoring.align_to_anchors`) so the arm is graded on relations, not its choice of SVG origin.

New 2D task suite `bench/tasks_2d.json` (8 tasks, 60 claims, UI/floor-plan layouts weighted dense
L2/L3), gold-pose validated. `bench/report.py` aggregates `results-<model>.json` files into a
cross-model table with the WITH-blind / blind-WITHOUT lift breakdown.

**Safety incident found and fixed:** `opencode run`'s default agent has blanket `*` tool permissions —
running DeepSeek through it wrote 3 stray `.svg` files into the repo root via unrequested Write/Bash
tool calls mid-completion. Fixed by pinning the transport to opencode's built-in `plan` agent (denies
edit/write outside its own scratch dir). Also added retry-with-backoff to both CLI transports after a
claude-cli call failed outright on a transient rate-limit hiccup under sustained back-to-back calls
(reproducible: none in isolation, real under the full sweep's call volume).

**Real numbers, Anthropic slate (claude-cli, hardened transport, k=3):** Haiku and Sonnet both **saturate
`tasks_2d.json`** — SVG/WITHOUT/WITH all 60/60 claims, BLIND 58–60/60. No lift observable: this suite has
no headroom left for either model, confirming the earlier pilot finding that the checker's lift only
shows where the baseline breaks. The opencode lane (GLM 5.2, DeepSeek v4 flash) did not complete this
session — died silently mid-run in the background-task environment; a **pre-hardening** run on those two
did show real lift (WITH − blind: GLM +15.0pp, DeepSeek +11.7pp) but ran under the agentic-write bug
above, so those specific numbers are not trustworthy and were not carried forward — re-run needed.

## Completed — 2026-07-19

### M1 W3 — thin kernel + deterministic checker
`checker/` scores `TOP · DIR · DIST · faces · align · quant · count · HOLD · Allen` on definite scenes,
O(n²), explicit tolerance on every predicate; three non-PASS verdicts (FAIL / ERROR / SKIPPED). CLI
`python -m checker examples/office.json`. Public repo **github.com/lsfcin/spacemantics** (MIT). 43 tests green.

### M1 W3c — checkability filter run
`dsl/CHECKABILITY.md` — the filter run as output, not intent: 15+ core concepts have a working predicate;
**4 core concepts demoted** for lacking one (PATH-shape, nested transforms, spatial arrays,
constraint-solving), each with a named restoration path.

### M1 W2b — surface v2 regeneration (complete)
`dsl/TYPES.md` (type ontology + intrinsic-front flag, mirrored in `checker/types.py`); `EXAMPLES.md`
rewritten in v2 prose (verbs + articles + setup/action/claim; fixed a v1 bug — `left of the desk` is legal,
the error case needs a frontless ground); `GRAMMAR-PROSE.ebnf` v2 (article rule now *syntactic* — `move a
ball` is a grammar error) + per-example parse trace; `GRAMMAR-JSON.md` regenerated against the **real**
checker AST; `SPEC.md` three-line-kinds + articles-as-identity; paper `sections/04_method.tex` dual-surface
+ surface ablation. Paper on texpace Overleaf (`6a5430c…`, ICLR 2026, `main`), recompiles 10pp, 0 undefined
citations.

### Checker 2D-profile fix
Honor the 2D profile per CONFLICTS C1: `above`/`below` map to +Y (not gravity +Z), and a 2D scene's Z is
flattened to an unbounded span so only X and Y decide topology/distance. Fixed two bugs found while
building the SVG render (above=+Z; thin 2D objects reading as EC under tolerance). 4 regression tests
(`tests/test_profile_2d.py`). Also: a claim about a missing entity now returns ERROR, not a crash.

### Visual WITH/WITHOUT pilot — bench/ + adapters/
`adapters/`: `texpace → SVG` (top-down footprints) with the checker's verdicts drawn on — objects that
break a claim are red, a panel lists PASS/FAIL. `bench/`: the WITH/WITHOUT harness — three arms (WITHOUT
one-shot · blind k-retries no-feedback control · WITH k-retries carrying checker verdicts), checker scores
all three; provider-agnostic model client; easy + hard-L3 task sets, feasibility-checked. Published visual
demo artifact.
**Pilot finding:** simple tasks are solved one-shot (no lift headroom); hard L3 tasks give the baseline
real headroom; but Gemini (off-slate, the only key in this environment) free-tier quota cannot sustain the
feedback loop. A real WITH/WITHOUT number needs an on-slate model (Claude / opencode).

## Completed — 2026-07-12

### Milestone 0.5 — texpace foundations (research before build)
Delegated deep research (5 sub-agents Q1–Q5) → `academy/papers/spacemantics/outputs/texpace-foundations.md`
(verdict + 28 verified refs). Sub-questions: frames of reference (Levinson → world/group/locale); QSR
calculi (RCC-8 topology, Rectangle Algebra direction, Allen time, STCC); spatial-language lexicon map
(+ Regier & Carlson AVS); prior DSLs/verification (SpatialGrammar, HDSL, Cassowary, Prepose+Z3); potential
verdict. Distilled into texpace v0 design principles (foundations §6).

### M1 W1 / W2 / W4 / W5
- **W1** `dsl/INVENTORY.md` + `INVENTORY-ADVISORY.md` + `CONFLICTS.md` (six convention conflicts + canonical choice).
- **W2** `dsl/SPEC.md` + `CONFORMANCE.md` (kernel · modules · profiles · adapters).
- **W4** `tasks/TAXONOMY.md` + `TAXONOMY-FAMILIES.md` — 13 families × 3 levels, literature-anchored.
- **W5** paper sections 02/03/04 + `lib/refs.bib` — compiles, 13pp, 0 undefined citations.
