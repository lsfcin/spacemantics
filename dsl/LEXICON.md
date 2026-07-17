# texpace — Controlled-English Lexicon (v2)
> The closed set of phrasings and what each one means. Anything not listed is a parse error, never a guess.

The **contract** between the prose surface and the checker. Deliberately **closed**: a phrasing outside
this document does not parse. We never infer intent — that is the Prepose discipline, and it is what keeps
the front end a *parser* rather than an *interpreter*.

Prose and JSON are two surfaces over one AST (see [SPEC.md](SPEC.md)). The predicate names in the right
column (`TOP`, `DIR`, RCC-8 codes) are the **IR** — the checker's vocabulary. Nobody writes them.

---

## 0. A document has three kinds of line

| Kind | Reads like | Ordered? | Role |
|---|---|---|---|
| **Setup** | `use meters and seconds as units.` | — | frame, units, tolerance, profile |
| **Action** | `add a chair in front of the desk.` | **yes** — a program | how the scene is built or edited |
| **Claim** | `no two objects overlap.` | no — a set | what must be true. **This is what the checker scores.** |

Actions are the *program*; claims are the *spec*. The checker evaluates every claim against the **final**
state. This split is what lets texpace express editing (inherently imperative) without giving up
verification (inherently declarative).

## 1. Setup

| Prose | Meaning |
|---|---|
| `this is a 2d \| 2.5d \| 3d \| 4d scene.` | profile |
| `use meters and seconds as units.` | length + time base (C2, C3) |
| `up is +Z.` / `the frame is right-handed.` | canonical frame (C1); the profile supplies a default |
| `positions are accurate to 5mm.` / `angles are accurate to 0.5deg.` | **tolerance — mandatory.** Without it nothing is verifiable |
| `view from (8, 8, 6) looking at the plaza, isometric, called ne_cam.` | camera / viewpoint |
| `the chair's height is free.` | underspecification — the checker will not score it |

One canonical phrasing per concept. We do **not** ship synonyms: every alias is another near-miss a model
can emit and another branch in the parser.

## 2. Articles are a type system on identity

This is the core of the surface, and it is checked, not conventional.

| Article | Meaning | Legal with |
|---|---|---|
| **`a` / `an`** | **introduces** a new object | `add`, `create` **only** |
| **`the`** | **refers to** an existing object | `move`, `delete`, `rotate`, `place`, and all claims |

```
add a ball of radius 10cm.        # 'a'  -> creates
move the ball onto the shelf.     # 'the' -> must already exist
```

**Rejected forms** (each is an error, never a silent guess):

```
move a ball.
  error: 'move' needs an existing object. Did you mean "the ball"?
         To create one, write "add a ball".

add the ball.
  error: 'add' introduces a new object — use "a ball".
```

The rejected `move a ball` is the important one. If it silently created a second ball, the scene would
fork invisibly and the error would surface far away (a failing object count, a phantom overlap). Silent,
non-local, plausible-looking — the worst class of bug. We refuse it.

**Uniqueness rule.** `the ball` is legal only if **exactly one** ball exists. Otherwise:

```
the ball
  error: 3 objects are balls. Disambiguate ("the red ball") or name them
         ("add a ball called target").
```

**Naming:** `add a ball called target.` → later referred to as `the target`.

## 3. Actions (the program)

Verbs desugar into `create` + `constrain`. Nothing new reaches the checker.

| Prose | Desugars to |
|---|---|
| `add a chair.` | `create(chair)` — position free |
| `add a chair in front of the desk.` | `create(chair)` + `constrain DIR(chair, desk, front, locale)` |
| `add a lamp on the desk.` | `create(lamp)` + `constrain TOP(lamp, desk, EC)` + support |
| `move the ball onto the shelf.` | `constrain TOP(ball, shelf, EC)` + support, on the existing ball |
| `move the ball 2m to the left.` | `constrain` a translation |
| `place \| put the crate inside the room.` | `constrain TOP(crate, room, NTPP)` |
| `rotate the desk 90 degrees.` | orientation update (quaternion; never stored as Euler — C4) |
| `point the camera at the plaza.` | orientation constraint |
| `attach \| connect the handle to the door.` | `constrain TOP(handle, door, EC)` + persistent |
| `align the chair with the desk.` | axis collinearity within tolerance |
| `delete \| remove the chair.` | destroy |

Any spatial preposition from §5–§7 may ride on any verb. That is where the readability comes from: the
verb says *what to do*, the preposition says *where*, and the preposition is already a checked predicate.

## 4. Claims (the spec — what the checker scores)

| Prose | Mode |
|---|---|
| `the chair faces the desk.` | **assertion** — a fact the checker verifies |
| `the chair must face the desk.` | **constraint** — a goal the model/solver must achieve |

Use a constraint when the spec states an outcome without saying how to reach it (generation tasks); an
assertion when checking a scene that already exists (verification tasks).

## 5. Topology — RCC-8

| Prose | IR |
|---|---|
| `A is clear of B` | `DC` — disconnected |
| `A touches B` | `EC` — boundaries meet, interiors disjoint |
| `A rests on B` / `A sits on B` / `... on B` | `EC` **+ support** (gravity-bearing) |
| `A overlaps B` | `PO` |
| `A is inside B` / `... into B` | `NTPP` — strictly interior, not touching the edge |
| `A is within B` | `TPP ∨ NTPP` — interior, may touch the edge |
| `A contains B` | inverse of `is within` |
| `A coincides with B` | `EQ` |

`is inside` vs `is within` is the one distinction users must learn — RCC-8 genuinely separates them, and
real specs depend on it (a tile flush against a wall vs floating clear of it).

## 6. Direction — and the frame rule

| Prose | IR |
|---|---|
| `A is above \| below B` | `DIR(vertical, world)` — gravity; never ambiguous |
| `A is north \| south \| east \| west of B` | `DIR(compass, world)` — absolute; never ambiguous |
| `A is left of \| right of \| in front of \| behind B` | `DIR(axis, ?)` — **frame required**, see below |
| `... seen from V` | anchor = `group{viewpoint: V}` |
| `... seen from V, mirrored \| rotated \| shifted` | relative-frame convention (default: mirrored — the English one) |

**The frame rule** — the arity gate, made grammatical:

1. `above`/`below`/compass are **world**-anchored. Always legal.
2. For `left of` / `right of` / `in front of` / `behind`:
   - **with** `seen from V` → **group** anchor. Legal.
   - **without**, and B **has an intrinsic front** → **locale** anchor. The natural English reading:
     *"the chair is in front of the desk"* means the desk's own front.
   - **without**, and B has **no** intrinsic front → **parse error**:
     `'ball' has no front — add "seen from <viewpoint>"`.

Case 3 is the commonest real spatial ambiguity, and English has it too: *"left of the ball"* is genuinely
meaningless without a viewpoint. texpace refuses to represent it rather than guessing. Underspecification
becomes *unwritable*, not merely wrong.

Which types have an intrinsic front is defined in [TYPES.md](TYPES.md), and is user-extensible.

## 7. Distance, alignment, motion

| Prose | IR |
|---|---|
| `A is within 2m of B` / `at least 2m from B` / `2m from B` | `DIST` vs tolerance |
| `A is near \| far from B` | `DIST` vs the declared threshold |
| `A faces B` / `A points at B` | angle(front axis of A, A→B) ≈ 0 — requires A to have a front |
| `A is aligned with \| flush with B` | axis/edge collinearity |
| `A is parallel to \| perpendicular to B` | angle between axes ≈ 0° / 90° |
| `A moves to \| toward \| away from B` | `PATH` |
| `A passes behind \| in front of \| over \| through B` | `PATH` with a shape constraint |
| `A enters \| leaves B` | `PATH` ⇒ finally `NTPP` / from `NTPP` to `DC` |
| `A comes to rest on B` | **outcome** — at rest, `EC` + support |

An **ordinal** quantity (CV depth, z-rank) may never appear in a distance predicate — that is a **type
error**, not a wrong answer (C2).

## 8. Time, negation, coverage

| Prose | IR |
|---|---|
| `... then ...` | `SEQ` — Allen `meets`/`before` |
| `... and ... / while ...` | `PAR` — Allen `overlaps`/`during` |
| `... or ...` | `ALT` — an acceptance set; **no geometric predicate** |
| `X before \| after \| during \| until Y` | Allen interval relations |
| `the ball at 1.2s is at (2m, 0, 1m).` | keyframe |
| `hold <claim> for 3s.` | `HOLD` — invariant over an interval |
| `repeat <action> 3 times.` | `REPEAT` — **temporal**; distinct from the spatial `repeat ... along` (C5) |
| `no two <set> overlap.` | `none(...)` |
| `every <x> in <set> rests on <y>.` | `every(...)` |
| `there are exactly N <set>.` | `count(...) = N` — **coverage**; stops a model from "solving" a scene by deleting objects |

On an **ordinal** timebase (`steps`), durations do not exist: `hold ... for 3s` is a **type error** (C3).

## 9. Extensions

| Prose | Module |
|---|---|
| `define a casa: ... end.` | `parametric` — a reusable module |
| `repeat the casa 7 times along +X spacing 3.45m, called the houses.` | `parametric` — **spatial** array (C5) |
| `the 7th house is a corner unit.` | per-instance override |
| `simulate physics with gravity -9.81.` | `physics` — **advisory**: executed, never scored |
| `quickly \| slowly \| suddenly \| smoothly \| directly` | dynamics — **advisory**; modifies execution, never the scored relation |

---

## Why closed

An open lexicon would need a model to interpret the prose, reintroducing exactly the non-determinism the
checker exists to remove. Closed means every sentence has exactly one meaning — the same meaning to a
human, a model, and the checker. That identity *is* the project. The cost is ~45 phrasings to learn; if
learning them ever feels like memorising rather than writing English, we drew the set wrong.
