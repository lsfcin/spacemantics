# Pilot runner: run WITHOUT / blind / WITH across the task set, print the results table, write results.json.

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .arms import ArmResult, run_blind, run_with, run_without, run_without_svg
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
    arms = _arm_names(header)
    rows = _run_all(tasks, header, model, k, arms)
    _print_table(rows, model, k, arms)
    _write(rows, model, k, arms)
    return 0


def _arm_names(header: dict) -> tuple:
    """The raw-SVG arm only exists where SVG can carry the scene — the 2D profile (no z in a footprint)."""
    if header.get("profile") == "2d":
        result = ("svg", "without", "blind", "with")
    else:
        result = ("without", "blind", "with")
    return result


def _run_arm(name: str, task: dict, header: dict, model: Model, k: int) -> ArmResult:
    if name == "svg":
        result = run_without_svg(task, header, model)
    elif name == "without":
        result = run_without(task, header, model)
    elif name == "blind":
        result = run_blind(task, header, model, k)
    else:
        result = run_with(task, header, model, k)
    return result


def _run_all(tasks: list, header: dict, model: Model, k: int, arms: tuple) -> list:
    rows = []
    for task in tasks:
        row = {"task": task["id"]}
        for name in arms:
            row[name] = _run_arm(name, task, header, model, k)
            _pause()
        rows.append(row)
        _print_row(row, arms)
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


def _print_row(row: dict, arms: tuple) -> None:
    cells = [f"{name.upper()} {_cell(row[name])}" for name in arms]
    line = f"{row['task']:<24} | " + " | ".join(cells)
    print(line)


def _print_table(rows: list, model: Model, k: int, arms: tuple) -> None:
    print("")
    print(f"=== texpace pilot — model {model.label()}, k={k}, {len(rows)} tasks ===")
    summary = _summary(rows, arms)
    for arm in arms:
        stats = summary[arm]
        line = (
            f"{arm.upper():<8}: solved {stats['solved']}/{stats['n']}"
            f"  |  claims {stats['passed']}/{stats['scored']}"
            f"  ({stats['claim_pct']:.0f}% of claims, {stats['solve_pct']:.0f}% of tasks)"
        )
        print(line)


def _summary(rows: list, arms: tuple) -> dict:
    summary = {}
    for arm in arms:
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


def _write(rows: list, model: Model, k: int, arms: tuple) -> None:
    payload = {
        "model": model.label(), "k": k,
        "summary": _summary(rows, arms),
        "rows": [_row_json(r, arms) for r in rows],
    }
    text = json.dumps(payload, indent=2)
    path = HERE / f"results-{_slug(model)}.json"
    path.write_text(text, encoding="utf-8")
    print(f"\nwrote {path}")


def _slug(model: Model) -> str:
    label = model.label()
    flat = label.replace(":", "-")
    result = flat.replace("/", "-")
    return result


def _row_json(row: dict, arms: tuple) -> dict:
    result = {"task": row["task"]}
    for arm in arms:
        item = row[arm]
        result[arm] = {
            "solved": item.solved, "passed": item.passed,
            "scored": item.scored, "attempts": item.attempts, "error": item.error,
        }
    return result


if __name__ == "__main__":
    raise SystemExit(main())
