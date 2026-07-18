# texpace — JSON Interchange Surface (v2)
> The JSON AST the checker actually consumes, bijective with GRAMMAR-PROSE.ebnf. This is the real schema — `examples/office.json` is a live instance.

This is **not** an invented interchange format: it is exactly what
[`../checker/loader.py`](../checker/loader.py) parses and
[`../checker/evaluate.py`](../checker/evaluate.py) scores. Prose and JSON are two surfaces over one AST;
the checker sees only the AST (SPEC §"Surfaces"). Run it: `python -m checker ../examples/office.json`.

## 1. Document

Nothing is implicit — a missing header field does not parse (SPEC §0, `loader._required`).

```json
{
  "texpace": "1.0",
  "profile": "2d | 2.5d | 3d | 4d",
  "frame":  { "handedness": "right", "up": "+Z", "forward": "+Y", "origin": "<name>" },
  "units":  { "length": "m", "angle": "rad", "dpi": 96, "cell_size_m": 1.5, "parent_extent_m": 1.0 },
  "timebase": "seconds | steps | months | frames",
  "tolerance": { "length": "5mm", "angle": "0.5deg", "time": "1ms" },
  "types":      [ { "name": "lectern", "parent": "furniture" } ],
  "entities":   [ /* §2 */ ],
  "viewpoints": [ /* §3 */ ],
  "events":     { "touch_shelf": [1.0, 1.02] },
  "claims":     [ /* §4 */ ]
}
```

- **`frame` must be canonical** — right-handed, `+Z` up, `+Y` forward (C1). A non-canonical frame is
  rejected at the door; the *adapter* converts, the checker never does (`loader._require_frame`).
- **`tolerance` is mandatory.** `units.dpi` / `cell_size_m` / `parent_extent_m` are only required when a
  device / grid / normalized unit is actually used (C2).
- **`types`** extends the base ontology of [TYPES.md](TYPES.md); `has_front` is inherited unless overridden.

## 2. Entity

```json
{
  "name": "chair", "type": "chair",
  "shape": { "kind": "box", "extent": [0.5, 0.5, 0.9] },   // or {"kind":"sphere","radius":0.1}, {"kind":"point"}
  "position": [0.0, 0.9, 0.45],
  "orientation": [1.0, 0.0, 0.0, 0.0],                     // unit quaternion (w,x,y,z); never Euler (C4)
  "keyframes": [ { "t": 0.0, "position": [-2,0,0.1], "orientation": [1,0,0,0] } ],
  "free": ["position.z"]                                   // declared-free DOF: reported, never scored
}
```

`orientation` defaults to identity; `keyframes` (when present) override the static pose and are
interpolated at the claim's instant. A prose `add a chair of size ...` desugars to one entity object; the
prose verb tail (`in front of the desk`) desugars to a **claim**, not into the entity.

## 3. Viewpoint

```json
{ "name": "ne_cam", "position": [8, 8, 6], "look_at": "plaza" }
```

Binds the **group** anchor. Prose `view from (8,8,6) looking at the plaza, isometric, called ne_cam.`

## 4. Claims — the scored AST

One object per claim. `"mode"` is `"assert"` (a fact, scored) or `"constrain"` (a goal, recorded);
`"at"` names an instant (seconds); `"text"` is the rendered prose the report echoes. Every claim carries a
`"pred"` **or** a `"quant"`/`"pred"` pair.

| Predicate object | Prose (LEXICON) |
|---|---|
| `{"pred":"TOP","a","b","rcc":["EC"]}` | `A rests on B` / `A is inside B` (rcc = the accepted RCC-8 codes) |
| `{"pred":"DIR","fig","gnd","term":"above","anchor":{"kind":"world"}}` | `A is above B` (world; compass too) |
| `{"pred":"DIR","fig","gnd","term":"front","anchor":{"kind":"locale"}}` | `A is in front of B` (B has a front) |
| `{"pred":"DIR","fig","gnd","term":"left","anchor":{"kind":"group","viewpoint":"ne_cam"}}` | `A is left of B seen from ne_cam` |
| `{"pred":"DIST","fig","gnd","op":"<","q":{"value":1.5,"unit":"m"}}` | `A is within 1.5m of B` |
| `{"pred":"FACES","a","b"}` | `A faces B` |
| `{"pred":"PARALLEL","a","b"}` / `{"pred":"PERPENDICULAR","a","b"}` | `A is parallel/perpendicular to B` |
| `{"pred":"ALIGNED","a","b","axis":"x"}` | `A is aligned with B` |
| `{"pred":"COUNT","set":{"type":"furniture"},"op":"==","n":2}` | `there are exactly 2 ...` (coverage) |
| `{"pred":"ALLEN","a","b","rel":"before|meets"}` | `A before B` — `a`,`b` are `events` keys |
| `{"pred":"HOLD","interval":[0,2],"claim":{...}}` | `hold <claim> for 2s` |
| `{"quant":"none","over":{"pairs":{"type":"thing"}},"pred":{"pred":"TOP","rcc":["PO","EQ","TPP","TPPi","NTPP","NTPPi"]}}` | `no two objects overlap` |
| `{"quant":"every","over":{"set":{"type":"furniture"},"as":"a"},"pred":{"pred":"TOP","b":"ball","rcc":["DC"]}}` | `every ... is clear of the ball` |

**Selectors** (`set`, `over.pairs`, `over.set`): `{"type":"<t>"}` matches the type and its subtypes;
`{"names":[...]}` matches an explicit list. `over.pairs` binds unordered pairs (the `no two` idiom);
`over.set` binds one variable named by `over.as`.

## 5. Bijection — the six examples' claims

Each scored prose line from [EXAMPLES.md](EXAMPLES.md) and the AST it desugars to.

| # | Prose (EXAMPLES.md) | JSON AST |
|---|---|---|
| 1 | `the title is within the card.` | `{"pred":"TOP","a":"title","b":"card","rcc":["TPP","NTPP"]}` |
| 1 | `the title is above the button.` | `{"pred":"DIR","fig":"title","gnd":"button","term":"above","anchor":{"kind":"world"}}` |
| 1 | `no two objects overlap.` | `{"quant":"none","over":{"pairs":{"type":"thing"}},"pred":{"pred":"TOP","rcc":["PO","EQ","TPP","TPPi","NTPP","NTPPi"]}}` |
| 2 | `the chair faces the desk.` | `{"pred":"FACES","a":"chair","b":"desk"}` |
| 2 | `the desk is left of the ball.` | `{"pred":"DIR","fig":"desk","gnd":"ball","term":"left","anchor":{"kind":"locale"}}` → **ERROR** (ball has no front) |
| 3 | `the token is left of the crate seen from ne_cam.` | `{"pred":"DIR","fig":"token","gnd":"crate","term":"left","anchor":{"kind":"group","viewpoint":"ne_cam"}}` |
| 4 | `every house in the houses rests on the terrain.` | `{"quant":"every","over":{"set":{"type":"house"},"as":"a"},"pred":{"pred":"TOP","b":"terrain","rcc":["EC"]}}` |
| 4 | `there are exactly 7 houses.` | `{"pred":"COUNT","set":{"type":"house"},"op":"==","n":7}` |
| 5 | `hold the ball is clear of the box for 0.3s.` | `{"pred":"HOLD","interval":[0,0.3],"claim":{"pred":"TOP","a":"ball","b":"box","rcc":["DC"]}}` |
| 6 | `the ball touches the box before the ball touches the shelf.` | `{"pred":"ALLEN","a":"touch_box","b":"touch_shelf","rel":"before|meets"}` |

The prose action `repeat the casa 7 times ...` is a **module/loader** concern, not a claim — it expands the
scene before any claim is scored (and is a demoted concept today, see [CHECKABILITY.md](CHECKABILITY.md)).

## 6. The checker consumes neither surface

The checker evaluates the AST both surfaces desugar to. Prose-vs-JSON is therefore a free experimental
variable, not a scoring dimension: which surface a model emits is an ablation axis in the benchmark (M2),
testing the project's own claim that the lift comes from the checker, not the notation.
