# The three experimental arms: WITHOUT (one-shot), blind-retry (control), WITH (checker feedback loop).

from __future__ import annotations

from dataclasses import dataclass

from adapters import parse_poses

from .model_client import Model, ModelError, complete
from .prompts import build_blind_retry, build_feedback, build_svg_task_prompt, build_task_prompt, extract_poses
from .scoring import ScoreResult, align_to_anchors, score_poses


@dataclass
class ArmResult:
    task_id: str
    solved: bool
    passed: int
    scored: int
    attempts: int
    error: str = ""


def run_without(task: dict, header: dict, model: Model) -> ArmResult:
    """WITHOUT texpace: one shot, no verifiable feedback. The baseline capability."""
    result = _one_attempt(task, header, model, build_task_prompt(task))
    return result


def run_without_svg(task: dict, header: dict, model: Model) -> ArmResult:
    """WITHOUT texpace, raw-format edition: one shot of plain SVG, parsed back for scoring. 2D tasks only.
    Parsed poses are anchor-aligned first: the arm is scored on relations, not on its choice of origin."""
    prompt = build_svg_task_prompt(task)

    def extract(text: str) -> dict:
        poses = parse_poses(text)
        result = align_to_anchors(task, poses)
        return result

    outcome = _attempt(task, header, model, prompt, extract)
    result = _merge(task, outcome, 1)
    return result


def run_blind(task: dict, header: dict, model: Model, k: int) -> ArmResult:
    """Control: k attempts, retried with NO checker information. Isolates 'more tries' from feedback."""
    result = _loop(task, header, model, k, feedback=False)
    return result


def run_with(task: dict, header: dict, model: Model, k: int) -> ArmResult:
    """WITH texpace: k attempts, each retry carries the checker's per-claim verdicts. The full loop."""
    result = _loop(task, header, model, k, feedback=True)
    return result


def _loop(task: dict, header: dict, model: Model, k: int, feedback: bool) -> ArmResult:
    base = build_task_prompt(task)
    prompt = base
    total = len(task["claims"])
    last = ArmResult(task["id"], solved=False, passed=0, scored=total, attempts=0, error="no attempt")
    for attempt in range(k):
        outcome = _attempt(task, header, model, prompt)
        last = _merge(task, outcome, attempt + 1)
        if outcome.solved:
            break
        prompt = _next_prompt(base, outcome, feedback)
    return last


def _next_prompt(base: str, outcome: "_Attempt", feedback: bool) -> str:
    """`complete` is single-turn, so every retry re-carries the full task + the previous answer."""
    if feedback and outcome.report is not None:
        nudge = build_feedback(outcome.report)
    else:
        nudge = build_blind_retry()
    result = f"{base}\n\nYour previous answer:\n{outcome.text}\n\n{nudge}"
    return result


@dataclass
class _Attempt:
    solved: bool
    score: ScoreResult | None
    report: object
    error: str
    text: str = ""


def _attempt(task: dict, header: dict, model: Model, prompt: str, extract=extract_poses) -> _Attempt:
    text = ""
    try:
        text = complete(model, prompt)
        poses = extract(text)
    except (ModelError, ValueError) as failure:
        return _Attempt(False, None, None, str(failure)[:120], text)
    score = score_poses(task, header, poses)
    result = _Attempt(score.solved, score, score.report, "", text)
    return result


def _one_attempt(task: dict, header: dict, model: Model, prompt: str) -> ArmResult:
    outcome = _attempt(task, header, model, prompt)
    result = _merge(task, outcome, 1)
    return result


def _merge(task: dict, outcome: _Attempt, attempts: int) -> ArmResult:
    """The denominator is ALWAYS the task's full claim count — an API/parse error scores 0/total, never 0/0."""
    total = len(task["claims"])
    if outcome.score is None:
        result = ArmResult(task["id"], False, 0, total, attempts, outcome.error)
        return result
    result = ArmResult(
        task["id"],
        solved=outcome.solved,
        passed=outcome.score.passed,
        scored=outcome.score.scored,
        attempts=attempts,
        error="",
    )
    return result
