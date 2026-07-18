# texpace — Worked Examples (v2 prose)
> Six examples, kernel-only → fully extended. Every line is a phrasing from the closed LEXICON v2. These are the parser's acceptance suite.

Every line below is legal [LEXICON.md](LEXICON.md) v2 prose — verbs, articles, periods. The IR column is
what the checker sees; prose and JSON are two surfaces over that one AST ([SPEC.md](SPEC.md)).

**Three kinds of line** (LEXICON §0, SPEC "Three kinds of line"): **setup** (frame/units/tolerance/view),
**action** (the ordered program that builds or edits the scene — verbs desugar to `create` + `constrain`),
**claim** (the unordered spec — *the only thing the checker scores*). Examples 1–2 are kernel-only; 3–6
each switch on exactly one module.

**Two attribute phrasings** carry size, extending LEXICON §3's `of radius`: `of radius 0.1m` (spheres) and
`of size 1 x 1 x 1m` (boxes). Both are checked attributes, not free text.

---

## 1. Kernel only — 2D UI layout (target: SVG)

Entities, topology, direction, negation, coverage. No camera, no time, no arrays.

```
# setup
this is a 2d scene.
use pixels as units.
positions are accurate to 2px.

# actions — the program
add a panel called card of size 400 x 320.
add a label called title of size 360 x 40.
add a control called button of size 120 x 40.

# claims — the spec (scored)
the title is within the card.
the button is within the card.
the title is above the button.
the button is at least 16px from the card.
no two objects overlap.
there are exactly 3 objects.
```

| Line | Kind | IR |
|---|---|---|
| `add a panel called card ...` | action | `create(card: panel)`; `called` binds the name so `the card` refers later (LEXICON §2) |
| `the title is within the card.` | claim | `TOP(title, card, TPP ∨ NTPP)` |
| `the title is above the button.` | claim | `DIR(title, button, above, world)` — gravity axis, needs no frame |
| `the button is at least 16px from the card.` | claim | `DIST(button, card) ≥ 16px` |
| `no two objects overlap.` | claim | `none(TOP(a,b,PO) for a,b in objects)` |
| `there are exactly 3 objects.` | claim | `count(objects) = 3` — coverage; stops "solving" the layout by deleting the button |

**Kernel sufficient?** Yes. `above` needs no frame — gravity fixes it.

## 2. Kernel only — the frame rule doing real work (target: glTF)

```
# setup
this is a 3d scene.
use meters as units.
positions are accurate to 5mm.
angles are accurate to 0.5deg.

# actions
add a desk.
add a ball of radius 0.1m.
add a chair in front of the desk.
add a lamp on the desk.

# claims
the chair faces the desk.
the desk is left of the ball.
```

The **articles** are checked: `add a desk` introduces; `the desk` refers. `move a ball` would be a parse
error (LEXICON §2). Two lines are the point of the example:

- `add a chair in front of the desk.` — **legal**. The desk *has an intrinsic front* ([TYPES.md](TYPES.md)),
  so `in front of` resolves against the desk's own front: the **locale** anchor. This is the natural
  English reading.
- `the desk is left of the ball.` — **parse error**. A ball has *no* front, so `left of the ball` has no
  frame to be read in. texpace refuses it rather than guessing:

```
error: 'ball' has no intrinsic front — 'left of the ball' is unreadable.
       add "seen from <viewpoint>".
```

This is the single commonest real spatial ambiguity, and the kernel catches it **before any geometry
runs**. (Contrast v1 of this doc, which wrongly flagged `left of the desk` — a desk *does* have a front, so
that one is legal. The frame rule keys on the **ground's** type, not on the word `left`.)

**Kernel sufficient?** Yes.

## 3. + `camera` module — 2.5D isometric (target: Tiled TMX)

The first extension. We need a camera because (a) `left of` needs a viewpoint and (b) **depth is derived
from the camera, never authored** (C6).

```
# setup
this is a 2.5d scene.
use meters as units.
positions are accurate to 1cm.

# actions
add a plaza of size 10 x 10m.
view from (8, 8, 6) looking at the plaza, isometric, called ne_cam.
add a token of radius 0.4m inside the plaza.
add a crate of size 1 x 1 x 1m.

# claims
the token is left of the crate seen from ne_cam.
the crate is in front of the token seen from ne_cam.
```

| Line | Kind | IR |
|---|---|---|
| `view from (8,8,6) looking at the plaza, ..., called ne_cam.` | setup | binds a viewpoint; enables the **group** anchor |
| `add a token ... inside the plaza.` | action | `create(token)` + `TOP(token, plaza, NTPP)` |
| `... left of the crate seen from ne_cam.` | claim | `DIR(token, crate, left, group{viewpoint: ne_cam})` — arity gate satisfied |
| `the crate is in front of the token seen from ne_cam.` | claim | occlusion order, **derived** from the camera, not authored |

`in front of ... seen from ne_cam` is exactly the claim isoroll's three conflicting depth formulas each
tried to express. Name the camera and the depth key is *derived* — `depth = dot(position, view_dir)` — so
there is nothing left to disagree about.

**Kernel sufficient?** No. Needs `camera` (+ `depth`, auto-on in the 2.5D profile).

## 4. + `parametric` module — the casinhas array (target: IFC)

The kernel cannot say "seven near-identical houses" without writing them seven times. This gap killed
texpace v0 (C5).

```
# setup
this is a 3d scene.
use meters as units.
positions are accurate to 1cm.
up is +Z.

# actions
define a casa:
  add a slab of size 3.45 x 12.5 x 0.12m.
  add a wall of size 3.45 x 0.15 x 2.8m on the slab.
end.
repeat the casa 7 times along +X spacing 3.45m, called the houses.
the 7th house is a corner unit.

# claims
every house in the houses rests on the terrain.
no two houses overlap.
there are exactly 7 houses.
```

| Line | Kind | IR |
|---|---|---|
| `define a casa: ... end.` | action | `parametric` module definition |
| `repeat the casa 7 times along +X spacing 3.45m, called the houses.` | action | **spatial** array — expanded, then every instance checked |
| `the 7th house is a corner unit.` | action | per-instance override (`houses[6]`) |
| `there are exactly 7 houses.` | claim | coverage — the model cannot quietly emit six |

This `repeat ... along` is **spatial**. The temporal `repeat <action> 3 times` (LEXICON §8) is a different
primitive; conflating them was the v0 defect.

**Kernel sufficient?** No. Needs `parametric` (+ `hierarchy` for the module's internal structure).

## 5. + `timeline` module — 2D animation, kinematic (target: Lottie)

```
# setup
this is a 4d scene.
use meters and seconds as units.
positions are accurate to 5mm.

# actions
add a ball of radius 0.1m.
add a box of size 1 x 1 x 1m.
the ball at 0.0s is at (0, 0, 1m).
the ball at 1.2s is at (2m, 0, 1m).

# claims
the ball passes behind the box then is clear of the box.
hold the ball is clear of the box for 0.3s.
```

| Line | Kind | IR |
|---|---|---|
| `the ball at 1.2s is at (2m, 0, 1m).` | action | keyframe |
| `... passes behind the box ...` | claim | `PATH(ball, box, behind)` — sampled per frame |
| `... then ...` | claim | `SEQ` — Allen `meets`/`before` |
| `hold the ball is clear of the box for 0.3s.` | claim | `HOLD(TOP(ball,box,DC), 0.3s)` — invariant over an interval |

Time is checked by decomposition: **per-frame spatial relations and inter-frame Allen relations are
verified separately**, each inside its tractable fragment — never as one joint network.

**Kernel sufficient?** No. Needs `timeline`. Still fully deterministic — no physics yet.

## 6. + `physics` — advisory, outcome-checked (target: glTF + engine)

The only example where something is *executed* rather than checked.

```
# setup
this is a 4d scene.
use meters and seconds as units.
positions are accurate to 5mm.
simulate physics with gravity -9.81.

# actions
add a ball of radius 0.1m.
add a box of size 0.3 x 0.3 x 0.3m.
add a shelf of size 1 x 0.3 x 0.05m.
the ball at 0s is at (0, 0, 2m).

# claims
the ball comes to rest on the shelf.
the ball touches the box before the ball touches the shelf.
```

| Line | Kind | IR |
|---|---|---|
| `simulate physics with gravity -9.81.` | setup | **advisory** — executed by the engine, never scored |
| `the ball comes to rest on the shelf.` | claim | **outcome**: at rest, `TOP(ball, shelf, EC)` + support |
| `the ball touches the box before the ball touches the shelf.` | claim | **outcome**: Allen order over contact events |

The simulation itself is **not** verified — engines disagree and are not reproducible. Only *observables*
are: the resting position and the Allen ordering of contact events, each within tolerance. `gravity -9.81`
is a fact about how the scene was executed, not a claim about it.

**Kernel sufficient?** No — and deliberately never fully checkable. That is what `advisory` means.

---

## The same document, JSON surface

Prose and JSON are bijective. Example 1's first three claims as JSON AST:

```json
{ "pred": "TOP", "a": "title", "b": "card", "rcc": ["TPP", "NTPP"] }
{ "pred": "DIR", "fig": "title", "gnd": "button", "term": "above", "anchor": {"kind": "world"} }
{ "quant": "none", "over": {"pairs": {"type": "thing"}},
  "pred": {"pred": "TOP", "rcc": ["PO", "EQ", "TPP", "TPPi", "NTPP", "NTPPi"]} }
```

The checker never sees either surface — it sees the AST both parse to. Which surface a model emits is a
free experimental variable: prose-vs-JSON is an ablation axis in the benchmark (M2), testing our own claim
that surface syntax is not the lever. The JSON here is exactly what
`python -m checker examples/office.json` consumes.
