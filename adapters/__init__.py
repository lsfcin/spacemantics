# adapters facade: render a texpace scene to a viewable open format, and parse one back for scoring.

from __future__ import annotations

from .svg import render_document, render_pair
from .svg_parse import parse_poses

__all__ = ["parse_poses", "render_document", "render_pair"]
