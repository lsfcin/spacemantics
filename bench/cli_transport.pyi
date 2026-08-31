from _typeshed import Incomplete

CLI_TIMEOUT_S: int
CLI_RETRIES: int
ANSI_PATTERN: Incomplete
OPENCODE_AGENT: str

class CliError(Exception): ...

def run_claude_cli(model_id: str, prompt: str) -> str: ...
def run_opencode(model_id: str, prompt: str) -> str: ...
