# CLI: `python -m adapters <scene.json>` -> an SVG (footprints + checker verdicts) on stdout.

from __future__ import annotations

import json
import sys
from pathlib import Path

from .svg import render_document


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python -m adapters <scene.json> [title]", file=sys.stderr)
        return 2
    path = args[0]
    title = args[1] if len(args) > 1 else Path(path).stem
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    svg = render_document(document, title)
    print(svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
