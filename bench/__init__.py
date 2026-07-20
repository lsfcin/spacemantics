# bench facade: the pilot WITH/WITHOUT harness. Load tasks, run arms against a model, score via the checker.

from __future__ import annotations

from .arms import ArmResult, run_blind, run_with, run_without, run_without_svg
from .model_client import Model, ModelError, complete
from .scoring import ScoreResult, score_poses

__all__ = [
    "ArmResult",
    "Model",
    "ModelError",
    "ScoreResult",
    "complete",
    "run_blind",
    "run_with",
    "run_without",
    "run_without_svg",
    "score_poses",
]
