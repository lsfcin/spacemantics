# Transports that shell out to local agent CLIs (claude -p, opencode run). Keeps model_client HTTP-only.

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time

CLI_TIMEOUT_S = 420
CLI_RETRIES = 3
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# opencode's default "build" agent has permission "*" allow "*" — it will happily invoke Write/Bash
# and touch the filesystem mid-completion (observed: it wrote stray .svg files into the repo). "plan"
# is a built-in agent that denies edit/write outside its own scratch dir, so a bench completion cannot
# leave files behind. This is a completion transport, not an agentic one — no tool use should persist.
OPENCODE_AGENT = "plan"


class CliError(Exception):
    """The CLI call failed (after retries), timed out, or returned no text."""


def run_claude_cli(model_id: str, prompt: str) -> str:
    """Complete via the local `claude` binary in print mode. Uses the login, no API key needed."""
    binary = _claude_binary()
    command = [binary, "-p", "--model", model_id, prompt]
    text = _run(command)
    return text


def run_opencode(model_id: str, prompt: str) -> str:
    """Complete via `opencode run --agent plan`. `model_id` is opencode's provider/model path."""
    binary = shutil.which("opencode")
    if not binary:
        raise CliError("opencode CLI not found on PATH")
    command = [binary, "run", "--agent", OPENCODE_AGENT, "-m", model_id, prompt]
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
    """Run from a neutral cwd so no project instructions/hooks leak into the completion. Retries on a
    non-zero exit or empty output — sustained back-to-back subscription-CLI calls hit transient
    rate-limit/session hiccups that a single attempt would wrongly score as a model failure."""
    last = "no attempt"
    for attempt in range(CLI_RETRIES):
        try:
            text = _attempt(command)
            return text
        except CliError as failure:
            last = str(failure)
            if attempt < CLI_RETRIES - 1:
                time.sleep(5.0 * (attempt + 1))
    raise CliError(f"failed after {CLI_RETRIES} attempts: {last}")


def _attempt(command: list[str]) -> str:
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
