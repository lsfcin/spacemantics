# Transports that shell out to local agent CLIs (claude -p, opencode run). Keeps model_client HTTP-only.

from __future__ import annotations

import os
import re
import shutil
import subprocess

CLI_TIMEOUT_S = 300
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class CliError(Exception):
    """The CLI call failed, timed out, or returned no text."""


def run_claude_cli(model_id: str, prompt: str) -> str:
    """Complete via the local `claude` binary in print mode. Uses the login, no API key needed."""
    binary = _claude_binary()
    command = [binary, "-p", "--model", model_id, prompt]
    text = _run(command)
    return text


def run_opencode(model_id: str, prompt: str) -> str:
    """Complete via `opencode run`. `model_id` is opencode's provider/model path (that slash is theirs)."""
    binary = shutil.which("opencode")
    if not binary:
        raise CliError("opencode CLI not found on PATH")
    command = [binary, "run", "-m", model_id, prompt]
    text = _run(command)
    return text


def _claude_binary() -> str:
    binary = shutil.which("claude")
    if not binary:
        binary = os.environ.get("CLAUDE_CODE_EXECPATH", "")
    if not binary:
        raise CliError("claude CLI not found (PATH or CLAUDE_CODE_EXECPATH)")
    return binary


def _run(command: list[str]) -> str:
    """Run from a neutral cwd so no project instructions/hooks leak into the completion."""
    try:
        outcome = subprocess.run(
            command, capture_output=True, text=True, timeout=CLI_TIMEOUT_S, cwd="/"
        )
    except subprocess.TimeoutExpired as failure:
        raise CliError(f"CLI timed out after {CLI_TIMEOUT_S}s") from failure
    if outcome.returncode != 0:
        detail = outcome.stderr.strip()
        raise CliError(f"CLI exit {outcome.returncode}: {detail[:200]}")
    text = _clean(outcome.stdout)
    if not text:
        raise CliError("empty CLI completion text")
    return text


def _clean(raw: str) -> str:
    stripped = ANSI_PATTERN.sub("", raw)
    result = stripped.strip()
    return result
