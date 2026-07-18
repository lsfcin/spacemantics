# Pilot runner: run WITHOUT / blind / WITH across the task set, print the results table, write results.json.

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .arms import ArmResult, run_blind, run_with, run_without
from .model_client import Model

HERE = Path(__file__).resolve().parent
PAUSE_S = 1.5


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bench", description="texpace WITH/WITHOUT pilot.")
    parser.add_argument("--model", default="gemini:gemini-2.5-flash")
    parser.add_argument("--k", type=int, default=3, help="max attempts for the retry arms")
    parser.add_argument("--limit", type=int, default=0, help="run only the first N tasks (0 = all)")
    parser.add_argument("--tasks", default="tasks.json", help="task-set filename under bench/")
    arguments = parser.parse_args(argv)
    status = _run(arguments.model, arguments.k, arguments.limit, arguments.tasks)
    return status


def _run(model_spec: str, k: int, limit: int, tasks_file: str) -> int:
    provider, model_id = model_spec.split(":", 1)
    model = Model(provider=provider, id=model_id)
    suite = json.loads((HERE / tasks_file).read_text(encoding="utf-8"))
    header = suite["header"]
    tasks = suite["tasks"]
    if limit > 0:
        tasks = tasks[:limit]
    rows = _run_all(tasks, header, model, k)
    _print_table(rows, model, k)
    _write(rows, model, k)
    return 0


def _run_all(tasks: list, header: dict, model: Model, k: int) -> list:
    rows = []
    for task in tasks:
        without = run_without(task, header, model)
        _pause()
        blind = run_blind(task, header, model, k)
        _pause()
        withfb = run_with(task, header, model, k)
        _pause()
        rows.append({"task": task["id"], "without": without, "blind": blind, "with": withfb})
        _print_row(rows[-1])
    return rows


def _pause() -> None:
    time.sleep(PAUSE_S)


def _cell(result: ArmResult) -> str:
    mark = "SOLVED" if result.solved else "  --  "
    detail = f"{result.passed}/{result.scored}"
    if result.error:
        detail = "ERR"
    text = f"{mark} {detail:>5} a{result.attempts}"
    return text


def _print_row(row: dict) -> None:
    line = f"{row['task']:<24} | WITHOUT {_cell(row['without'])} | BLIND {_cell(row['blind'])} | WITH {_cell(row['with'])}"
    print(line)


def _print_table(rows: list, model: Model, k: int) -> None:
    print("")
    print(f"=== texpace pilot — model {model.label()}, k={k}, {len(rows)} tasks ===")
    summary = _summary(rows)
    for arm in ("without", "blind", "with"):
        stats = summary[arm]
        line = (
            f"{arm.upper():<8}: solved {stats['solved']}/{stats['n']}"
            f"  |  claims {stats['passed']}/{stats['scored']}"
            f"  ({stats['claim_pct']:.0f}% of claims, {stats['solve_pct']:.0f}% of tasks)"
        )
        print(line)


def _summary(rows: list) -> dict:
    summary = {}
    for arm in ("without", "blind", "with"):
        summary[arm] = _arm_stats(rows, arm)
    return summary


def _arm_stats(rows: list, arm: str) -> dict:
    n = len(rows)
    solved = sum(1 for r in rows if r[arm].solved)
    passed = sum(r[arm].passed for r in rows)
    scored = sum(r[arm].scored for r in rows)
    claim_pct = 0.0 if scored == 0 else 100.0 * passed / scored
    solve_pct = 0.0 if n == 0 else 100.0 * solved / n
    stats = {
        "n": n, "solved": solved, "passed": passed, "scored": scored,
        "claim_pct": claim_pct, "solve_pct": solve_pct,
    }
    return stats


def _write(rows: list, model: Model, k: int) -> None:
    payload = {
        "model": model.label(), "k": k,
        "summary": _summary(rows),
        "rows": [_row_json(r) for r in rows],
    }
    text = json.dumps(payload, indent=2)
    path = HERE / "results.json"
    path.write_text(text, encoding="utf-8")
    print(f"\nwrote {path}")


def _row_json(row: dict) -> dict:
    result = {"task": row["task"]}
    for arm in ("without", "blind", "with"):
        item = row[arm]
        result[arm] = {
            "solved": item.solved, "passed": item.passed,
            "scored": item.scored, "attempts": item.attempts, "error": item.error,
        }
    return result


if __name__ == "__main__":
    raise SystemExit(main())
