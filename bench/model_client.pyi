from dataclasses import dataclass

TIMEOUT_S: int

@dataclass(frozen=True)
class Model:
    provider: str
    id: str
    def label(self) -> str: ...

class ModelError(Exception): ...

def complete(model: Model, prompt: str, temperature: float = 0.2) -> str: ...
