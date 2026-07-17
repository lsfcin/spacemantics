# CLI: `python -m checker <scene.json>` -> the report, exit 0 iff every scored claim passes.

from __future__ import annotations

import argparse
import sys

from .evaluate import check_scene
from .loader import load_scene
from .scene import SceneError
from .units import UnitTypeError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="texpace-check", description="Score a texpace scene's claims.")
    parser.add_argument("scene", help="path to a texpace JSON scene")
    parser.add_argument("--quiet", action="store_true", help="print only the summary line")
    arguments = parser.parse_args(argv)
    status = _run(arguments.scene, arguments.quiet)
    return status


def _run(path: str, quiet: bool) -> int:
    try:
        scene = load_scene(path)
    except (SceneError, UnitTypeError) as failure:
        print(f"parse error: {failure}", file=sys.stderr)
        return 2
    report = check_scene(scene)
    if quiet:
        print(report.summary())
    else:
        rendered = report.render()
        print(rendered)
    passed = report.passed()
    status = 0 if passed else 1
    return status


if __name__ == "__main__":
    code = main()
    sys.exit(code)
