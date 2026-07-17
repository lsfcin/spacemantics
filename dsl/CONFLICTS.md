# texpace — Conventions Reconciliation
> The six convention conflicts found across real backends, and texpace's canonical choice for each

Every conflict below was found in **our own workspace**, not invented. The reconciliation strategy is the
same in each case and is the core design move:

> **texpace never adopts a backend's convention. It requires an explicit declaration, normalizes to one
> canonical internal form, evaluates all relations there, and lets each adapter emit its own native form.**

This is what makes the cross-format consistency test possible: one scene emitted to SVG and to glTF must
parse back to the *same* canonical form and therefore score *identically*. If it doesn't, the adapter is
wrong — not the checker.

---

## C1 — Frames: up-axis, handedness, origin anchor

| Backend | Native frame |
|---|---|
| IFC (ISO 16739), Blender | **Z-up**, right-handed, +Y north |
| glTF 2.0 | **Y-up**, right-handed, −Z forward |
| SVG, PPTX | 2D, **Y-down**, origin **top-left** |
| Foundry / PIXI (isoroll) | 2D screen, Y-down, but **bottom-left anchor** for tiles |
| corpora (OpenCV camera) | **Y-down**, +Z forward *into* the scene |

The trap: SVG/PPTX and Foundry are *both* Y-down yet disagree on the **anchor corner**, so content
authored top-left silently mirrors when placed bottom-left. isoroll's `swapSide` bug (B28) is exactly
this class.

**Canonical form.** Right-handed · **+Z up (gravity)** · +X east · +Y north · origin at a declared datum.
Chosen to match IFC and Blender — our highest-stakes 3D consumers, and an ISO standard. glTF's Y-up is a
single fixed, well-known basis swap at the adapter.

**Rule.** Every document declares its frame (`handedness`, `up`, `forward`, `origin`). Every adapter is a
bijection to canonical. **Relations are only ever evaluated in canonical form.** The 2D profile is the
canonical XY plane viewed from +Z, so "above" means +Y everywhere — the SVG/PPTX adapters flip Y on the
way in and out. Screen space is never a texpace frame.

## C2 — Units: six incommensurable, one of them not a magnitude at all

metres (IFC) · EMU, 9144000×5143500 (PPTX) · % of parent (PPTX layout) · px (SVG, PIXI) · grid cells /
voxels (Foundry, isoroll) · **relative/inverse depth (corpora — unitless)**. Plus pt for stroke weights.

**Canonical form.** Every length is a **unit-tagged quantity**. There is no bare scalar "length".

| Unit kind | Examples | Usable in metric predicates? |
|---|---|---|
| `metric` | m, mm | yes (SI canonical: metres) |
| `device` | px, EMU, pt | yes, once a resolution/DPI is declared |
| `normalized` | fraction of parent ∈ [0,1] | yes, once the parent extent is known |
| `grid` | cell, voxel | yes — **only** if the document declares the cell's physical size |
| **`ordinal`** | corpora relative depth, z-index rank | **NO — magnitude does not exist** |

**The ordinal rule (load-bearing).** An `ordinal` quantity carries rank, not magnitude. It may be used in
ordinal predicates (`in-front-of`, `behind`, z-order) and **never** in a metric one. `DIST(a,b) < 2m`
over an ordinal depth is a **type error**, not a wrong answer. This comes straight from `code/corpora`,
whose DepthAnythingV2 path yields *relative/inverse* depth with a hardcoded focal length: it can honestly
verify "A is in front of B" and cannot verify "A is 2.4 m from B". Typing this into the language is how we
avoid silently fabricating metric claims from CV.

**Note.** isoroll declares 1 voxel = 1.5 m, but `DEFAULT_WALL_H` is 3 in content and 2 in the painter —
a live divergence. texpace forces a single declaration; the divergence becomes a parse error.

## C3 — Time: four bases, no shared clock

| Backend | Time base | Hazard |
|---|---|---|
| shortvid | integer **frame index** at a *mutable* fps | an fps override silently retimes every existing index |
| casinhas 4D | calendar **months** | not SI seconds; calendar arithmetic |
| Slides | ordinal **click-steps** (`v-click`) | no duration exists at all |
| glTF / Lottie | seconds | — |

**Canonical form.** Continuous **τ in SI seconds**. Every document declares a
`timebase ∈ {seconds | frames@fps | steps | months}`; the adapter converts.

**The ordinal rule again, for time.** A `steps` timebase is **ordinal**: it supports Allen *order*
relations (`before`, `meets`, `after`) and **not** durations. `HOLD(pred, Δ)` on an ordinal timebase is a
**type error**. `months` is a *calendar* timebase: durations exist but obey calendar arithmetic, not SI
seconds. Frame indices are **never** canonical — texpace stores seconds and emits indices at adapt time,
so a later fps change cannot retime existing content.

## C4 — Rotation: four representations

Slides *derives* degrees from a shear/scale matrix (`rotation_deg = atan2(shearY, scaleX)`) · Foundry
stores rotation+skew **projection presets** · IFC uses **direction cosines** (no Euler at all) · corpora
uses a raw direction vector.

**Canonical form.** Orientation is a **unit quaternion** (equivalently an orthonormal basis). texpace
**never** stores or round-trips Euler degrees: Euler loses information, and its sign convention silently
inverts under Y-down. Adapters *emit* whatever their format wants; nothing round-trips through degrees.

**Corollary that kills a bug class:** a projection preset (rotation + skew, e.g. isoroll's
`dimetric_2_1`) **is not an entity orientation** — it is a **camera/projection descriptor**. It lives in
the camera module, never in an entity's transform. isoroll conflates the two; texpace forbids it.

## C5 — Repetition: three mechanisms, none shared

casinhas needs a **7× parametric array** with a distinct corner case · PPTX has nested groups + affine
composition · Foundry has per-filename image presets. And texpace v0's only `REPEAT` was **temporal**.

**Canonical form.** A first-class **spatial array** in the parametric module, distinct from the temporal
`REPEAT(action, N)`:

```
array houses of <module> count 7 along +X spacing 3.45m
  override [6] { kind: corner_unit }
```

- Layouts: linear rank · 2D grid · along-path.
- **Per-instance overrides** (casinhas' corner unit).
- Instances get stable derived identities (`houses[3]`) so selectors can address them.

Conflating spatial and temporal repetition was the v0 gap; they are different primitives.

## C6 — Depth / z-order (internal: isoroll disagrees with itself)

Three coexisting formulas in one project:

| Site | Key | Implied camera |
|---|---|---|
| live runtime (`src/render/iso-tile-depth.ts`) | `(row − col + elev) * 10000 + band` | NE |
| dormant `DepthSorter` | `x + y + elev` | SE |
| occluder `_hasTokenBehind` | `x + y + elev` | SE |

They disagree because **each silently assumes a different camera**.

**Canonical form.** **Depth is derived, never authored.** texpace authors positions in the canonical
frame plus an explicit **camera**; the painter/depth key is *derived* as `depth = dot(position, view_dir)`
(plus a declared tie-break band). For the NE dimetric camera this reduces exactly to `(row − col + elev)`;
for the SE camera it reduces to `(x + y + elev)`. **The two isoroll formulas are the same formula under
different cameras** — which is precisely why they conflict, and why naming the camera fixes it.

An authored `layer` / `priority` remains available as an explicit tie-break, never as the primary order.

---

## Why this is a contribution, not plumbing

The reconciliation yields three falsifiable claims the paper can test:

1. **Cross-format consistency** — one scene emitted to two formats scores identically. If not, the
   adapter is wrong; the checker is the arbiter.
2. **Type-safety over magnitude** — ordinal quantities (CV depth, click-steps) cannot leak into metric
   predicates, so the system cannot fabricate metric claims it has no basis for.
3. **Convention bugs become parse errors** — isoroll's three depth conventions, its 3-vs-2 wall height and
   its 4-vs-5 stair steps are *detected*, not debated. Adopting texpace would fix real shipped bugs —
   the dogfood evidence (benchmark family 13).
