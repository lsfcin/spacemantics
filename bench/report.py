# Aggregate results-<model>.json files into one cross-model table, with the honest lift (WITH - blind).

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARM_ORDER = ("svg", "without", "blind", "with")


def main() -> int:
    files = sorted(HERE.glob("results-*.json"))
    if not files:
        print("no results-*.json files yet")
        return 1
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _print_model(payload)
    return 0


def _print_model(payload: dict) -> None:
    summary = payload["summary"]
    arms = [arm for arm in ARM_ORDER if arm in summary]
    print(f"\n=== {payload['model']} (k={payload['k']}, {summary[arms[0]]['n']} tasks) ===")
    for arm in arms:
        stats = summary[arm]
        line = (
            f"  {arm.upper():<8} claims {stats['passed']:>3}/{stats['scored']:<3}"
            f" ({stats['claim_pct']:5.1f}%)   solved {stats['solved']}/{stats['n']}"
            f" ({stats['solve_pct']:5.1f}%)"
        )
        print(line)
    _print_lift(summary)


def _print_lift(summary: dict) -> None:
    """WITH - blind is the checker's own contribution; blind - WITHOUT is what mere retries buy."""
    if "with" in summary and "blind" in summary:
        feedback = summary["with"]["claim_pct"] - summary["blind"]["claim_pct"]
        print(f"  lift (WITH - blind):      {feedback:+5.1f}pp of claims")
    if "blind" in summary and "without" in summary:
        retries = summary["blind"]["claim_pct"] - summary["without"]["claim_pct"]
        print(f"  lift (blind - WITHOUT):   {retries:+5.1f}pp of claims")


if __name__ == "__main__":
    raise SystemExit(main())
