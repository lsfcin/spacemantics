# The three experimental arms: WITHOUT (one-shot), blind-retry (control), WITH (checker feedback loop).

from __future__ import annotations

from dataclasses import dataclass

from .model_client import Model, ModelError, complete
from .prompts import build_blind_retry, build_feedback, build_task_prompt, extract_poses
from .scoring import ScoreResult, score_poses


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


def run_blind(task: dict, header: dict, model: Model, k: int) -> ArmResult:
    """Control: k attempts, retried with NO checker information. Isolates 'more tries' from feedback."""
    result = _loop(task, header, model, k, feedback=False)
    return result


def run_with(task: dict, header: dict, model: Model, k: int) -> ArmResult:
    """WITH texpace: k attempts, each retry carries the checker's per-claim verdicts. The full loop."""
    result = _loop(task, header, model, k, feedback=True)
    return result


def _loop(task: dict, header: dict, model: Model, k: int, feedback: bool) -> ArmResult:
    prompt = build_task_prompt(task)
    total = len(task["claims"])
    last = ArmResult(task["id"], solved=False, passed=0, scored=total, attempts=0, error="no attempt")
    for attempt in range(k):
        outcome = _attempt(task, header, model, prompt)
        last = _merge(task, outcome, attempt + 1)
        if outcome.solved:
            break
        prompt = _next_prompt(task, outcome, feedback)
    return last


def _next_prompt(task: dict, outcome: "_Attempt", feedback: bool) -> str:
    if feedback and outcome.report is not None:
        result = build_feedback(outcome.report)
    else:
        result = build_blind_retry("")
    return result


@dataclass
class _Attempt:
    solved: bool
    score: ScoreResult | None
    report: object
    error: str


def _attempt(task: dict, header: dict, model: Model, prompt: str) -> _Attempt:
    try:
        text = complete(model, prompt)
        poses = extract_poses(text)
    except (ModelError, ValueError) as failure:
        return _Attempt(False, None, None, str(failure)[:120])
    score = score_poses(task, header, poses)
    result = _Attempt(score.solved, score, score.report, "")
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
