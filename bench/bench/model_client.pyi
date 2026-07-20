from .cli_transport import CliError as CliError, run_claude_cli as run_claude_cli, run_opencode as run_opencode
from dataclasses import dataclass

TIMEOUT_S: int
RATE_LIMIT_RETRIES: int

@dataclass(frozen=True)
class Model:
    provider: str
    id: str
    def label(self) -> str: ...

class ModelError(Exception): ...

def complete(model: Model, prompt: str, temperature: float = 0.2) -> str: ...
