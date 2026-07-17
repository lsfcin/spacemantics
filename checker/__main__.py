# Module entrypoint so the checker runs as `python -m checker <scene.json>`.

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    code = main()
    sys.exit(code)
