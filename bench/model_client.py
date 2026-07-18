# Provider-agnostic text-completion client. Provider is data (a string), never baked into a file/verb name.

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

TIMEOUT_S = 60
RATE_LIMIT_RETRIES = 4


@dataclass(frozen=True)
class Model:
    """A model under test. `provider` selects the transport; `id` is the provider's model name."""

    provider: str
    id: str

    def label(self) -> str:
        result = f"{self.provider}:{self.id}"
        return result


class ModelError(Exception):
    """The provider call failed or returned no text."""


def complete(model: Model, prompt: str, temperature: float = 0.2) -> str:
    """Single-turn completion. Dispatches on `model.provider`; add a branch to widen the slate."""
    if model.provider == "gemini":
        result = _gemini(model.id, prompt, temperature)
    else:
        raise ModelError(f"no transport for provider '{model.provider}'")
    return result


def _gemini(model_id: str, prompt: str, temperature: float) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ModelError("GEMINI_API_KEY is not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    text = _send(request)
    return text


def _send(request: urllib.request.Request) -> str:
    raw = _send_with_backoff(request)
    result = _extract(raw)
    return result


def _send_with_backoff(request: urllib.request.Request) -> bytes:
    """Free-tier endpoints throttle hard; retry 429 with exponential backoff instead of failing the run."""
    delay = 4.0
    last = "no attempt"
    for attempt in range(RATE_LIMIT_RETRIES):
        try:
            handle = urllib.request.urlopen(request, timeout=TIMEOUT_S)
            raw = handle.read()
            return raw
        except urllib.error.HTTPError as failure:
            detail = failure.read().decode("utf-8", "replace")[:200]
            last = f"HTTP {failure.code}: {detail}"
            transient = failure.code in (429, 500, 503)
            if not transient:
                raise ModelError(last) from failure
            time.sleep(delay)
            delay = delay * 2
        except urllib.error.URLError as failure:
            raise ModelError(f"network error: {failure}") from failure
    raise ModelError(f"rate-limited after {RATE_LIMIT_RETRIES} retries: {last}")


def _extract(raw: bytes) -> str:
    data = json.loads(raw)
    candidates = data.get("candidates", [])
    if not candidates:
        raise ModelError(f"no candidates in response: {str(data)[:200]}")
    parts = candidates[0].get("content", {}).get("parts", [{}])
    text = parts[0].get("text", "")
    if not text:
        raise ModelError("empty completion text")
    return text
