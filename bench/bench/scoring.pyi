from _typeshed import Incomplete
from checker import CheckReport as CheckReport
from dataclasses import dataclass

CANONICAL_FRAME: Incomplete
IDENTITY: Incomplete

@dataclass(frozen=True)
class ScoreResult:
    passed: int
    scored: int
    solved: bool
    report: CheckReport
    def fraction(self) -> float: ...

def build_document(task: dict, header: dict, poses: dict) -> dict: ...
def score_poses(task: dict, header: dict, poses: dict) -> ScoreResult: ...
