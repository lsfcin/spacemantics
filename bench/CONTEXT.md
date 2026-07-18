# bench
> The WITH/WITHOUT pilot: does the checker-in-the-loop lift a model's spatial placement? Same tasks, same scorer, three arms.
> spec: none
> goal: [spacemantics](../../../brain/goals/spacemantics.md)

**What this measures.** The project's thesis is that the *checker*, not the notation, carries the lift
(surface syntax moves accuracy <1%, [CHECKABILITY.md](../dsl/CHECKABILITY.md)). So the pilot holds the
output format constant (the model emits a JSON pose per object) and toggles the **checker feedback loop**:

| Arm | What the model gets | Isolates |
|---|---|---|
| **WITHOUT** | one shot, no feedback | baseline spatial capability |
| **blind** | *k* attempts, retried with "try again" and no detail | the value of *extra tries alone* (the control) |
| **WITH** | *k* attempts, each retry carries the checker's per-claim verdicts | the value of **verifiable feedback** |

`WITH − blind` is the honest lift: the improvement that is the checker's feedback, not just more attempts.
`blind − WITHOUT` is what retries alone buy. The checker is the **scorer for all three arms** — that is the
whole point: it owns geometric truth, so it grades the baseline and drives the loop with the same predicates.

## Run

```bash
GEMINI_API_KEY=... python -m bench.run --k 3            # all tasks, 3 attempts
python -m bench.run --limit 2 --k 3                     # smoke test
```

Writes `results.json`; prints a per-task row + a summary (claims-passed % and tasks-solved %).

## Files

| File | Owns |
|---|---|
| [tasks.json](tasks.json) | the pilot task set — NL prompt + fixed anchors + **ground-truth claims** (the spec) |
| [model_client.py](model_client.py) | provider-agnostic completion; provider is data (`gemini` today), not a filename |
| [prompts.py](prompts.py) | the three messages (task / blind-retry / checker-feedback) + the pose extractor |
| [scoring.py](scoring.py) | build a scene from the model's poses, score it with the checker (shared by all arms) |
| [arms.py](arms.py) | the three arms as a single loop parametrized by feedback on/off |
| [run.py](run.py) | orchestrate arms × tasks, print the table, write `results.json` |

## Honesty notes

- **Pilot model = Gemini** only because it is the key present in this environment. The planned slate
  (Claude Haiku/Sonnet/Opus/Fable + opencode GLM/DeepSeek, ROADMAP M2) plugs in via one `model_client`
  branch — provider is a string, nothing else changes.
- **Tolerances are generous** (5 cm / 10°) so the signal is *getting the relation right*, not sub-mm
  precision. Tightening them is a separate difficulty axis (the L3 levels in [tasks/](../tasks/)).
- This is a **pilot**, not the M2 benchmark: hand-built tasks, one model, no format round-trip (glTF/SVG
  emit is M2). It exists to see the WITH/WITHOUT signal early, on real model calls, scored by the real checker.

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`__init__.py`](__init__.py) | — | — | **facade** — bench facade: the pilot WITH/WITHOUT harness. Load tasks, run arms against a model, score via the checker. |
| [`arms.py`](arms.py) | — | `ArmResult`, `run_without`, `run_blind`, `run_with` | The three experimental arms: WITHOUT (one-shot), blind-retry (control), WITH (checker feedback loop). |
| [`model_client.py`](model_client.py) | [`model_client.pyi`](model_client.pyi) | `Model`, `ModelError`, `complete`, `label` | Provider-agnostic text-completion client. Provider is data (a string), never baked into a file/verb name. |
| [`prompts.py`](prompts.py) | — | `build_task_prompt`, `build_blind_retry`, `build_feedback`, `extract_poses` | The three message builders (task prompt, blind-retry nudge, checker feedback) and the pose extractor. |
| [`run.py`](run.py) | — | `main` | Pilot runner: run WITHOUT / blind / WITH across the task set, print the results table, write results.json. |
| [`scoring.py`](scoring.py) | — | `ScoreResult`, `build_document`, `score_poses`, `fraction` | Score a model's placement: build a texpace document from the task + the model's poses, then run the checker. |
<!-- routing:end -->
