# texpace — Worked Examples
> Graded from kernel-only to fully extended. Each example states which modules it needs and why.

Phrasings come from the closed [LEXICON.md](LEXICON.md). The IR column is what the checker sees; prose
and JSON are two surfaces over the same AST.

**Reading guide:** examples 1–2 need **nothing but the kernel**. Examples 3–6 each switch on exactly one
more module, so you can see what each extension buys.

---

## 1. Kernel only — 2D UI layout (target: SVG)

Everything here is kernel: entities, topology, direction, negation, coverage. No camera, no time, no
arrays, no hierarchy.

```
scene login_form in 2d
  units px
  tolerance length 2px, angle 1deg

  a card   is a panel   sized 400 x 320
  a title  is a label   sized 360 x 40
  a button is a control sized 120 x 40

  title  is within card
  button is within card
  title  is above button
  button is at least 16px from card
  no two elements overlap
  there are exactly 3 elements within card
```

| Prose line | IR |
|---|---|
| `title is within card` | `TOP(title, card, TPP ∨ NTPP)` |
| `title is above button` | `DIR(title, button, vertical, world)` — gravity axis, unambiguous |
| `button is at least 16px from card` | `DIST(button, card) ≥ 16px` |
| `no two elements overlap` | `none(TOP(a,b,PO) for a,b in elements)` |
| `there are exactly 3 elements within card` | `count(...) = 3` — the coverage constraint that stops the model from "solving" the layout by deleting the button |

**Kernel sufficient?** Yes. Note `above` needs no frame — gravity fixes it. Nothing here is ambiguous.

## 2. Kernel only — the frame rule doing real work

```
scene desk_setup in 3d
  units meters
  tolerance length 5mm, angle 0.5deg

  a desk  is a desk   sized 1.6 x 0.8 x 0.75m     # a desk HAS an intrinsic front
  a chair is a chair  sized 0.5 x 0.5 x 0.9m
  a ball  is a prop   with radius 0.1m            # a ball has NO intrinsic front

  chair is in front of desk          # OK -> locale anchor (the desk's own front)
  chair faces desk
  lamp  rests on desk                # -> TOP(EC) + support
  ball  is left of desk              # ERROR: 'left of' needs a frame; desk's front doesn't fix left/right
```

The last line is the interesting one. English speakers make this mistake constantly. texpace refuses it:

```
parse error: 'left of' is viewpoint-relative and no viewpoint is bound.
  add: "ball is left of desk seen from <viewpoint>"
```

**Kernel sufficient?** Yes — and the kernel is where the ambiguity gets caught, before any geometry runs.

## 3. + `camera` module — 2.5D isometric (target: Tiled TMX)

The first extension. We need a camera because (a) `left of` requires a viewpoint and (b) **depth is
derived from the camera, never authored** (C6).

```
scene plaza in 2.5d
  units meters
  view ne_cam from (8, 8, 6) looking at plaza, isometric dimetric

  a token is a prop with radius 0.4m
  a crate is a box  sized 1 x 1 x 1m

  token is within plaza
  token is left of crate seen from ne_cam      # group anchor -> arity gate satisfied
  crate is in front of token seen from ne_cam  # so is this: occlusion order, derived not authored
```

`crate is in front of token seen from ne_cam` is exactly the claim isoroll's three conflicting depth
formulas were each trying to express. Here the camera is named, so the depth key is *derived* —
`depth = dot(position, view_dir)` — and there is nothing left to disagree about.

**Kernel sufficient?** No. Needs `camera` (+ `depth`, which the 2.5D profile switches on automatically).

## 4. + `parametric` module — the casinhas array (target: IFC)

The kernel cannot express "seven near-identical houses" without writing them out seven times. This is the
gap that killed texpace v0.

```
scene casinhas in 3d
  units meters
  frame up +Z right-handed
  let W = 3.45m

  module casa
    a slab  is a slab sized W x 12.5m x 0.12m
    a wall  is a wall sized W x 0.15m x 2.8m
    wall rests on slab
  end

  repeat casa 7 times along +X spacing W as houses
  houses[6] is a corner_unit                 # per-instance override

  every house in houses rests on terrain
  no two houses overlap
  there are exactly 7 houses
```

| Prose | IR |
|---|---|
| `repeat casa 7 times along +X spacing W` | **spatial** array — expanded, then every instance checked |
| `houses[6] is a corner_unit` | per-instance override (the real corner unit differs) |
| `there are exactly 7 houses` | coverage — the model cannot quietly emit six |

Note this `repeat` is **spatial**. The temporal `repeat <action> 3 times` (§7 of the lexicon) is a
different primitive. Conflating them was the v0 defect (C5).

**Kernel sufficient?** No. Needs `parametric` (+ `hierarchy` for the module's internal structure).

## 5. + `timeline` module — 2D animation, kinematic (target: Lottie)

```
scene ball_roll in 4d
  units meters, seconds
  tolerance length 5mm, angle 0.5deg

  a ball is a prop with radius 0.1m
  a box  is a box  sized 1 x 1 x 1m

  ball at 0.0s is at (0, 0, 1m)
  ball at 1.2s is at (2m, 0, 1m)

  ball passes behind box then is left of box seen from cam
  hold ball is clear of box for 0.3s
```

| Prose | IR |
|---|---|
| `ball at 1.2s is at (...)` | keyframe |
| `passes behind box` | `PATH(ball, box, behind)` — verified per-frame |
| `then` | `SEQ` — Allen `meets`/`before` |
| `hold ... for 0.3s` | `HOLD(TOP(ball,box,DC), 0.3s)` — invariant across an interval |

Time is checked by the STCC decomposition: **per-frame spatial relations and inter-frame Allen relations
are verified separately**, each inside its tractable fragment — never as one joint network.

**Kernel sufficient?** No. Needs `timeline`. (Still fully deterministic — no physics yet.)

## 6. + `physics` — advisory, outcome-checked (target: glTF + engine)

The only example where something is *executed* rather than checked.

```
scene drop in 4d
  units meters, seconds
  physics bullet, gravity -9.81        # ADVISORY: executed by the engine, never scored

  a ball  is a prop with radius 0.1m
  a shelf is a shelf sized 1 x 0.3 x 0.05m
  ball at 0s is at (0, 0, 2m)

  ball comes to rest on shelf                        # OUTCOME - checked
  ball touches box before ball touches shelf         # OUTCOME - Allen order over events
```

The simulation itself is **not** verified — engines disagree and are not reproducible. Only
**observables** are: the resting position (`TOP(ball, shelf, EC)` + support) and the Allen ordering of
contact events, each within tolerance. `gravity -9.81` is never scored; it is a fact about how the scene
was executed, not a claim about it.

**Kernel sufficient?** No — and deliberately, this one is never fully checkable. That is what `advisory`
means.

---

## The same document, JSON surface

Prose and JSON are bijective. Example 1's third assertion:

```json
{ "kind": "assert", "rel": "within",
  "figure": "title", "ground": "card", "anchor": "world" }
{ "kind": "assert", "rel": "dir", "axis": "vertical",
  "figure": "title", "ground": "button", "anchor": "world" }
{ "kind": "assert", "quantifier": "none", "rel": "overlaps",
  "over": {"a": "elements", "b": "elements"} }
```

The checker never sees either surface — it sees the AST both parse to. Which surface a model emits is
therefore a free experimental variable, and we treat it as one: prose-vs-JSON is an ablation axis in the
benchmark, testing our own claim that surface syntax is not the lever.
