# texpace — Type Ontology
> The closed base-type lattice carrying the intrinsic-front flag that gates the `locale` anchor (LEXICON §6).

## Why this exists

`left of` / `right of` / `in front of` / `behind` need a facing to resolve without a viewpoint. Whether a
type supplies one — **has an intrinsic front** — is the single boolean that gates the `locale` anchor
(SPEC.md §1.2, LEXICON §6 "The frame rule"). This file is the closed base ontology; §3 below gives the
phrasing for extending it. The flag lives on the **ground** of a direction claim, not the figure — see §4.

## 1. Root types with an intrinsic front

Anything with a facing edge or a canonical forward direction.

| Type | Supertype | Has intrinsic front? | Notes |
|---|---|---|---|
| `furniture` | — | yes | root: has a designed-in front (a face you approach) |
| `desk` | `furniture` | yes (inherited) | |
| `chair` | `furniture` | yes (inherited) | seat faces away from its backrest |
| `table` | `furniture` | yes (inherited) | |
| `lectern` | `furniture` | yes (inherited) | the worked user-extension example, §3 |
| `opening` | — | yes | root: faces the space it opens into |
| `door` | `opening` | yes (inherited) | |
| `window` | `opening` | yes (inherited) | |
| `vehicle` | — | yes | root: has a direction of travel |
| `car` | `vehicle` | yes (inherited) | |
| `agent` | — | yes | root: has a gaze/heading |
| `person` | `agent` | yes (inherited) | |
| `architectural` | — | yes | root: has a side it fronts |
| `wall` | `architectural` | yes (inherited) | faces the room/side it fronts |

## 2. Root types with no intrinsic front

Nothing about the geometry privileges one horizontal direction over another.

| Type | Supertype | Has intrinsic front? | Notes |
|---|---|---|---|
| `prop` | — | no | root: an inert object with no facing edge |
| `ball` | `prop` | no (inherited) | |
| `sphere` | `prop` | no (inherited) | |
| `panel` | `prop` | no (inherited) | |
| `crate` | `prop` | no (inherited) | |
| `box` | `prop` | no (inherited) | |
| `region` | — | no | root: a bounded area, not an oriented object |
| `room` | `region` | no (inherited) | |
| `plaza` | `region` | no (inherited) | |
| `surface` | — | no | root: a flat ground/support element |
| `slab` | `surface` | no (inherited) | |
| `terrain` | `surface` | no (inherited) | |
| `tile` | `surface` | no (inherited) | |

**Default.** A type not in this table inherits `prop` (no front) until declared otherwise (§3). This keeps
the base ontology small and closed without making every unlisted, scene-specific noun a parse error — the
alternative (reject unknown types outright) would break `add a <ident>.`'s generality for one-off nouns
(`token`, `lamp`, `handle`, `shelf`, `camera-mount`, ... — see EXAMPLES.md). Defaulting to **no** front, not
**has** front, is the safe direction: a spurious front produces a spurious locale-anchor reading (silently
wrong), while a missing front only ever escalates a direction claim to a parse error demanding
`seen from <viewpoint>` — loud, not silent, exactly the failure mode LEXICON §2 already prefers for
identity.

## 3. Extending the lattice

Subtype an existing root or branch — the flag is inherited, not re-declared:

```
a lectern is a kind of furniture.
```

Declare a brand-new root — this is the one place the flag must be stated explicitly, because there is no
supertype to inherit it from:

```
a lectern is a kind of thing with a front.
```

(A new root with no front is the same sentence minus the trailer: `a lectern is a kind of thing.` — the
absence of "with a front" is what makes it `prop`-like, matching the default in §2.)

## 4. What the flag does not do

It gates exactly one thing: whether `locale` is a legal anchor for `left of` / `right of` / `in front of` /
`behind`, evaluated against this type when it plays **ground** (SPEC.md §1.2, LEXICON §6). It does **not**
touch:

- `above` / `below` — vertical, gravity-anchored. Always legal, on any type, as figure or ground.
- compass (`north` / `south` / `east` / `west` of) — absolute, world-anchored. Always legal, on any type.
- the `group` anchor (`seen from V`) — legal on **any** ground, fronted or not, once a viewpoint is bound;
  the flag is irrelevant once a viewpoint exists.
- `TOP` (topology) and `DIST` (distance) predicates — no directionality to disambiguate, so nothing to gate.

Only the unqualified, viewpoint-free `left of` / `right of` / `in front of` / `behind` reads this flag.
