# texpace — JSON Interchange Surface
> Schema-shaped spec + round-trip table for the JSON surface, bijective with GRAMMAR-PROSE.ebnf over the same AST.

Derived mechanically from the JSON fragments already given at the end of `EXAMPLES.md` ("The same
document, JSON surface") plus the AST described in `SPEC.md` §1 (kernel), §1.2 (anchors/arity gate),
§1.7 (time), §2 (modules), §3 (physics). Field names (`kind`, `rel`, `figure`, `ground`, `anchor`)
continue the naming EXAMPLES.md already established — nothing here is a fresh vocabulary.

## 1. The statement envelope

```json
{
  "kind": "assert | constrain",
  "quantifier": "none | every | count",
  "over": { "var": "<ident>?", "set": "<ident>", "qualifier": { "rel": "within|in", "ground": "<ident>" } },
  "count": "<integer>",
  "rel": "clear_of | touches | rests_on | sits_on | overlaps | inside | within | contains | coincides |
          dir | dist_within | dist_at_least | dist_eq | near | far |
          faces | points_at | aligned | flush | parallel | perpendicular |
          moves_to | moves_toward | moves_away | passes_behind | passes_front | passes_over |
          passes_through | enters | leaves | comes_to_rest",
  "figure": "<ident>",
  "ground": "<ident>",
  "anchor": "world | locale | { \"group\": { \"viewpoint\": \"<ident>\", \"transform\": \"reflected|rotated|translated\" } }",
  "axis": "vertical | north | south | east | west | left | right | front | behind",
  "quantity": { "value": "<number>", "unit": "m|mm|px|cells|s|ms|deg" },
  "rcc8": "DC | EC | PO | TPP | TPPi | NTPP | NTPPi | EQ",
  "temporal": {
    "at": "<quantity>", "over": ["<quantity>", "<quantity>"],
    "allen": "before | after | during | until", "lhs": "<statement>", "rhs": "<statement>",
    "seq": ["<statement>", "..."],
    "hold": { "pred": "<statement>", "duration": "<quantity>" },
    "repeat": { "action": "<ident>", "times": "<integer>" }
  },
  "keyframe": { "entity": "<ident>", "t": "<quantity>", "position": ["<number|quantity>", "x3"] },
  "array": {
    "module": "<ident>", "count": "<integer>", "axis": "<signed-axis>", "spacing": "<quantity|ident>",
    "as": "<ident>", "overrides": [{ "index": "<integer>", "type": "<ident>" }]
  },
  "outcome": "<boolean>",
  "physics": { "advisory": true, "engine": "<ident>", "gravity": "<number>" }
}
```

Every field is optional except `kind`; which fields co-occur is determined by `rel`/`quantifier`/
`temporal` the same way the prose grammar's non-terminals gate which tail follows which head (e.g.
`rel: "dir"` requires `axis` and `anchor`; `quantifier: "count"` requires `count` and `over`, not `rel`).

## 2. Field reference

| Field | Closed values | Prose-side origin |
|---|---|---|
| `kind` | `assert`, `constrain` | LEXICON §9 (bare statement vs `must`) |
| `rel` | the ~25 relation names above | LEXICON §2-6 verb/copula phrasings |
| `anchor` | `world`, `locale`, `group{viewpoint,transform}` | LEXICON §3 frame rule; SPEC §1.2 arity gate |
| `axis` | `vertical`, compass 4, `left/right/front/behind` | LEXICON §3 `dir_tail` |
| `quantity.unit` | `m mm px cells s ms deg` | LEXICON quantities throughout |
| `rcc8` | RCC-8 eight-set | LEXICON §2 table |
| `quantifier` | `none`, `every`, `count` | LEXICON §8 |
| `temporal.allen` | `before after during until` | LEXICON §7 |
| `outcome` | boolean flag on a statement | SPEC §3 (physics observables only) |

## 3. Round-trip table

The bijection contract: each prose line from `EXAMPLES.md` and the JSON it desugars to.

| # | Prose (verbatim from EXAMPLES.md) | JSON AST |
|---|---|---|
| 1 | `title is within card` | `{"kind":"assert","rel":"within","figure":"title","ground":"card","anchor":"world"}` |
| 2 | `title is above button` | `{"kind":"assert","rel":"dir","axis":"vertical","figure":"title","ground":"button","anchor":"world"}` |
| 3 | `button is at least 16px from card` | `{"kind":"assert","rel":"dist_at_least","figure":"button","ground":"card","quantity":{"value":16,"unit":"px"}}` |
| 4 | `no two elements overlap` | `{"kind":"assert","quantifier":"none","rel":"overlaps","over":{"a":"elements","b":"elements"}}` |
| 5 | `there are exactly 3 elements within card` | `{"kind":"assert","quantifier":"count","count":3,"over":{"set":"elements","qualifier":{"rel":"within","ground":"card"}}}` |
| 6 | `chair is in front of desk` | `{"kind":"assert","rel":"dir","axis":"front","figure":"chair","ground":"desk","anchor":"locale"}` |
| 7 | `chair faces desk` | `{"kind":"assert","rel":"faces","figure":"chair","ground":"desk"}` |
| 8 | `lamp rests on desk` | `{"kind":"assert","rel":"rests_on","figure":"lamp","ground":"desk","rcc8":"EC"}` |
| 9 | `token is left of crate seen from ne_cam` | `{"kind":"assert","rel":"dir","axis":"left","figure":"token","ground":"crate","anchor":{"group":{"viewpoint":"ne_cam","transform":"reflected"}}}` |
| 10 | `every house in houses rests on terrain` | `{"kind":"assert","quantifier":"every","over":{"var":"house","set":"houses"},"rel":"rests_on","ground":"terrain"}` |
| 11 | `ball passes behind box then is left of box seen from cam` | `{"kind":"assert","temporal":{"seq":[{"rel":"passes_behind","figure":"ball","ground":"box"},{"rel":"dir","axis":"left","figure":"ball","ground":"box","anchor":{"group":{"viewpoint":"cam","transform":"reflected"}}}]}}` |
| 12 | `hold ball is clear of box for 0.3s` | `{"kind":"assert","temporal":{"hold":{"pred":{"rel":"clear_of","figure":"ball","ground":"box"},"duration":{"value":0.3,"unit":"s"}}}}` |
| 13 | `ball comes to rest on shelf` | `{"kind":"assert","rel":"comes_to_rest","figure":"ball","ground":"shelf","rcc8":"EC","outcome":true}` |
| 14 | `ball touches box before ball touches shelf` | `{"kind":"assert","temporal":{"allen":"before","lhs":{"rel":"touches","figure":"ball","ground":"box"},"rhs":{"rel":"touches","figure":"ball","ground":"shelf"}},"outcome":true}` |

Rows 13-14 carry `"outcome": true` because they sit under `physics bullet, gravity -9.81` in example 6
(SPEC §3): the simulation that produced them is advisory and unscored, but the resting position and
the Allen ordering of contact events are observables the checker does verify.

The spatial array (`repeat casa 7 times along +X spacing W as houses` + `houses[6] is a corner_unit`,
example 4) desugars to a single `array` object rather than a `statement`:
`{"array":{"module":"casa","count":7,"axis":"+X","spacing":"W","as":"houses","overrides":[{"index":6,"type":"corner_unit"}]}}`.

## 4. The checker consumes neither surface

The checker never parses prose or JSON directly — it evaluates the AST both surfaces desugar to
(`SPEC.md` §1.3-1.7). Prose-vs-JSON is therefore a free experimental variable, not a scoring dimension:
which surface a model is asked to emit is an ablation axis in the benchmark, testing the project's own
claim that the capability lift comes from the checker, not the grammar surface.
