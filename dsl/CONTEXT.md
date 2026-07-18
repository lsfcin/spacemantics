# texpace DSL
> The texpace language: concept inventory, conventions reconciliation, spec, grammar, adapter conformance
> spec: SPEC.md

Design home of **texpace** (text + space): a spatial *and* temporal DSL whose every kernel construct is
mechanically checkable.

**Governing principle** (from the M0.5 research): the capability lift comes from the **checker**, not the
grammar surface. So the grammar exists to make a model's spatial commitments *addressable and verifiable*
— and nothing enters the kernel without a checker predicate.

## Reading order

| # | File | What it answers |
|---|---|---|
| 1 | [EXAMPLES.md](EXAMPLES.md) | **Start here.** Six worked examples, kernel-only → fully extended. Shows what the language *feels* like |
| 2 | [LEXICON.md](LEXICON.md) | The closed controlled-English lexicon: every legal phrasing → the predicate it means |
| 3 | [SPEC.md](SPEC.md) | The language: two surfaces, one AST; kernel · modules · profiles · adapters |
| 4 | [INVENTORY.md](INVENTORY.md) | Which concepts are `core` / `module` — each with the predicate that checks it |
| 5 | [INVENTORY-ADVISORY.md](INVENTORY-ADVISORY.md) | Which concepts the filter **rejected**, and why (physics, rigging, appearance, aesthetics) |
| 6 | [CONFLICTS.md](CONFLICTS.md) | The six conventions conflicts (frames, units, time, rotation, repetition, depth) and the canonical choice for each |
| 7 | [GRAMMAR-PROSE.ebnf](GRAMMAR-PROSE.ebnf) · [GRAMMAR-JSON.md](GRAMMAR-JSON.md) | The two surfaces, formally |
| 8 | [CONFORMANCE.md](CONFORMANCE.md) | Adapter contract; conformance levels; the acceptance test; per-format capability matrix |

## If you only need one thing

- *"What does it look like?"* → [EXAMPLES.md](EXAMPLES.md)
- *"What may I write?"* → [LEXICON.md](LEXICON.md) — it is **closed**; anything else is a parse error
- *"Why is it shaped this way?"* → [CONFLICTS.md](CONFLICTS.md) — the reconciliation is the contribution
- *"Can texpace express X?"* → [INVENTORY.md](INVENTORY.md), then [CONFORMANCE.md](CONFORMANCE.md) §6

**Two surfaces, one AST:** controlled-English *prose* (humans, models) and *JSON* (tooling) are bijective;
the checker sees only the AST. Which surface a model emits is an experimental variable, not a bet.

Grounding: `academy/papers/spacemantics/outputs/texpace-foundations.md` (research verdict + v0 principles).

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`CHECKABILITY.md`](CHECKABILITY.md) | — | — | texpace — Checkability Filter (enforced) |
| [`CONFLICTS.md`](CONFLICTS.md) | — | — | texpace — Conventions Reconciliation |
| [`CONFORMANCE.md`](CONFORMANCE.md) | — | — | texpace — Adapter Conformance |
| [`EXAMPLES.md`](EXAMPLES.md) | — | — | texpace — Worked Examples (v2 prose) |
| [`GRAMMAR-JSON.md`](GRAMMAR-JSON.md) | — | — | texpace — JSON Interchange Surface (v2) |
| [`INVENTORY-ADVISORY.md`](INVENTORY-ADVISORY.md) | — | — | texpace — Concept Inventory: advisory and out-of-scope |
| [`INVENTORY.md`](INVENTORY.md) | — | — | texpace — Concept Inventory |
| [`LEXICON.md`](LEXICON.md) | — | — | texpace — Controlled-English Lexicon (v2) |
| [`SPEC.md`](SPEC.md) | — | — | SPEC: texpace DSL |
| [`TYPES.md`](TYPES.md) | — | — | texpace — Type Ontology |
<!-- routing:end -->
