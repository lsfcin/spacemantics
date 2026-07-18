from .model_client import Model as Model, ModelError as ModelError, complete as complete
from .prompts import build_blind_retry as build_blind_retry, build_feedback as build_feedback, build_task_prompt as build_task_prompt, extract_poses as extract_poses
from .scoring import ScoreResult as ScoreResult, score_poses as score_poses
from dataclasses import dataclass

@dataclass
class ArmResult:
    task_id: str
    solved: bool
    passed: int
    scored: int
    attempts: int
    error: str = ...

def run_without(task: dict, header: dict, model: Model) -> ArmResult: ...
def run_blind(task: dict, header: dict, model: Model, k: int) -> ArmResult: ...
def run_with(task: dict, header: dict, model: Model, k: int) -> ArmResult: ...

@dataclass
class _Attempt:
    solved: bool
    score: ScoreResult | None
    report: object
    error: str
