# The type ontology and the intrinsic-front flag: the one bit that gates locale-anchored direction (LEXICON §6, dsl/TYPES.md).

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TypeDef:
    name: str
    parent: str | None
    has_front: bool | None = None  # None = inherit from the parent


# The base ontology. Kept in lockstep with dsl/TYPES.md; a document may extend it, never contradict it.
BASE: tuple[TypeDef, ...] = (
    TypeDef("thing", None, has_front=False),
    TypeDef("furniture", "thing", has_front=True),
    TypeDef("desk", "furniture"),
    TypeDef("chair", "furniture"),
    TypeDef("table", "furniture"),
    TypeDef("lectern", "furniture"),
    TypeDef("opening", "thing", has_front=True),
    TypeDef("door", "opening"),
    TypeDef("window", "opening"),
    TypeDef("wall", "thing", has_front=True),
    TypeDef("vehicle", "thing", has_front=True),
    TypeDef("car", "vehicle"),
    TypeDef("person", "thing", has_front=True),
    TypeDef("camera", "thing", has_front=True),
    TypeDef("prop", "thing", has_front=False),
    TypeDef("ball", "prop"),
    TypeDef("crate", "prop"),
    TypeDef("panel", "prop"),
    TypeDef("lamp", "prop"),
    TypeDef("region", "thing", has_front=False),
    TypeDef("room", "region"),
    TypeDef("plaza", "region"),
    TypeDef("slab", "thing", has_front=False),
    TypeDef("terrain", "slab"),
    TypeDef("tile", "slab"),
    TypeDef("shelf", "thing", has_front=True),
    TypeDef("house", "thing", has_front=True),
)


class TypeError_(Exception):
    """An unknown type, or a type used where its flags forbid it."""


@dataclass
class Ontology:
    defs: dict[str, TypeDef] = field(default_factory=dict)

    def add(self, definition: TypeDef) -> None:
        parent = definition.parent
        if parent is not None and parent not in self.defs:
            raise TypeError_(f"unknown supertype '{parent}' for '{definition.name}'")
        self.defs[definition.name] = definition

    def has_front(self, name: str) -> bool:
        """Walk to the nearest ancestor that declares the flag. Every chain terminates at `thing`.

        An unlisted type inherits `prop` (no front) per TYPES.md §2 — the safe direction: a missing front
        only ever escalates a bare `left of` to a loud parse error, never a silent wrong locale reading.
        """
        current = self.defs.get(name)
        if current is None:
            return False
        while current.has_front is None:
            parent_name = current.parent
            if parent_name is None:
                raise TypeError_(f"type '{name}' has no intrinsic-front flag anywhere in its chain")
            current = self.defs[parent_name]
        result = bool(current.has_front)
        return result


def base_ontology() -> Ontology:
    ontology = Ontology()
    for definition in BASE:
        ontology.add(definition)
    return ontology
