from dataclasses import dataclass, field

@dataclass(frozen=True)
class TypeDef:
    name: str
    parent: str | None
    has_front: bool | None = ...

BASE: tuple[TypeDef, ...]

class TypeError_(Exception): ...

@dataclass
class Ontology:
    defs: dict[str, TypeDef] = field(default_factory=dict)
    def add(self, definition: TypeDef) -> None: ...
    def has_front(self, name: str) -> bool: ...

def base_ontology() -> Ontology: ...
