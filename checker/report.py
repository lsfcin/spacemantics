# The verdict record and the report. The checker's whole output surface: one line per claim, plus the scene's free DOFs.

from __future__ import annotations

from dataclasses import dataclass, field

PASS = "PASS"
FAIL = "FAIL"
ERROR = "ERROR"  # the claim is not evaluable as written (type error, arity gate) — never silently a FAIL
SKIPPED = "SKIPPED"  # declared free: the checker will not score it

SYMBOL: dict[str, str] = {PASS: "ok  ", FAIL: "FAIL", ERROR: "ERR ", SKIPPED: "skip"}


@dataclass(frozen=True)
class Verdict:
    status: str
    mode: str  # 'assert' (a fact, scored) | 'constrain' (a goal, reported)
    text: str  # the claim, rendered
    detail: str


@dataclass
class CheckReport:
    verdicts: list[Verdict] = field(default_factory=list)
    free_dofs: tuple[str, ...] = ()

    def add(self, verdict: Verdict) -> None:
        self.verdicts.append(verdict)

    def scored(self) -> list[Verdict]:
        result = [v for v in self.verdicts if v.mode == "assert"]
        return result

    def failures(self) -> list[Verdict]:
        result = [v for v in self.verdicts if v.status in (FAIL, ERROR)]
        return result

    def passed(self) -> bool:
        broken = self.failures()
        result = len(broken) == 0
        return result

    def summary(self) -> str:
        counts = {PASS: 0, FAIL: 0, ERROR: 0, SKIPPED: 0}
        for verdict in self.verdicts:
            counts[verdict.status] += 1
        result = (
            f"{counts[PASS]} pass, {counts[FAIL]} fail, "
            f"{counts[ERROR]} error, {counts[SKIPPED]} skipped "
            f"({len(self.free_dofs)} free DOF)"
        )
        return result

    def render(self) -> str:
        lines = []
        for verdict in self.verdicts:
            symbol = SYMBOL[verdict.status]
            lines.append(f"[{symbol}] {verdict.text}")
            if verdict.detail:
                lines.append(f"         {verdict.detail}")
        lines.append("")
        lines.append(self.summary())
        result = "\n".join(lines)
        return result
