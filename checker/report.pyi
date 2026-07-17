from dataclasses import dataclass, field

PASS: str
FAIL: str
ERROR: str
SKIPPED: str
SYMBOL: dict[str, str]

@dataclass(frozen=True)
class Verdict:
    status: str
    mode: str
    text: str
    detail: str

@dataclass
class CheckReport:
    verdicts: list[Verdict] = field(default_factory=list)
    free_dofs: tuple[str, ...] = ...
    def add(self, verdict: Verdict) -> None: ...
    def scored(self) -> list[Verdict]: ...
    def failures(self) -> list[Verdict]: ...
    def passed(self) -> bool: ...
    def summary(self) -> str: ...
    def render(self) -> str: ...
