# adapters facade: render a texpace scene to a viewable open format. SVG first (2D, needs no engine).

from __future__ import annotations

from .svg import render_document, render_pair

__all__ = ["render_document", "render_pair"]
