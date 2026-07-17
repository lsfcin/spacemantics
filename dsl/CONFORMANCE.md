# texpace — Adapter Conformance
> What an adapter must declare and support to carry canonical texpace scenes losslessly

Derived from [SPEC.md](SPEC.md) §5 (adapters are a bijection to canonical form) and
[CONFLICTS.md](CONFLICTS.md) (the six conventions every adapter crosses). An adapter that cannot state
every field in §1 is not conformant at any level.

## 1. Declaration block (every adapter, mandatory)

```
adapter <format> {
  frame     { handedness: ..., up: ..., forward: ..., origin: <corner|datum> }  # C1
  units     { length: <unit>, factor_to_m: <number> }                          # C2
  timebase  <seconds|frames@fps|steps|months>                                  # C3
  rotation  <quaternion|euler-shear|direction-cosines|angle-2d|none>           # C4, emitted form
  modules   [ <module>, ... ]                                                  # subset of §2 SPEC.md
  profile   [ <2d|2.5d|3d|4d>, ... ]                                           # supported profile(s)
  level     <L1|L2|L3>
}
```
Origin/anchor corner matters independently of handedness (C1): two Y-down formats can still disagree
on corner and silently mirror content. Units must include the conversion factor to metres (or state
`ordinal` — no factor exists).

## 2. Conformance levels

- **L1 — kernel-only.** Round-trips entities, geometry primitives, transforms (position + quaternion
  orientation + scale), anchors, and enough data for the checker to evaluate `DIR`/`DIST`/`TOP`/`PATH`
  in canonical form. Declares §1 fully. No module required.
- **L2 — kernel + profile-required modules.** Adds whatever SPEC.md §4 lists as live for the profile(s)
  it claims (e.g. a `2.5d` adapter must carry `camera(ortho/iso)`, `depth`, `hierarchy`, `parametric`).
  A profile claim without its required modules is a false conformance claim.
- **L3 — full, including advisory passthrough.** L2 plus best-effort carry of `appearance` and
  `physics`/outcome data even though neither is scored — round-trips them opaquely rather than dropping
  them.

## 3. Per-format conformance

| Format | Native frame | Native units | Native timebase | Rotation rep | Modules carried | Cannot represent |
|---|---|---|---|---|---|---|
| SVG | 2D, Y-down, origin top-left | px (device) | none (static); SMIL: seconds | 2D angle (`rotate`/skew), single axis | camera(ortho, via viewBox) · depth(paint order) · hierarchy(`<g>`) · appearance | 3D geometry; quaternion orientation; true parametric arrays (must pre-expand `array`); physics |
| PPTX/OOXML | 2D, Y-down, origin top-left | EMU (914400/in) | none native; animation timing: ms | 2D angle, 60,000ths-of-a-degree, single axis | hierarchy(grouped shapes) · appearance | 3D geometry; quaternion; **z-order is document order only** — no independent z field; parametric arrays (no native repeat, must expand); physics |
| Tiled TMX/TMJ | 2D grid, Y-down, origin top-left (isometric = diamond transform of same grid) | cell/tile (grid) | none native; tile-animation frame duration: ms | orthogonal flips only (H/V/diag) — no continuous rotation | depth(layer stack + explicit priority tie-break) · hierarchy(layers/groups) · camera(2.5d iso projection only) | true 3D; continuous rotation beyond 90° flips; perspective camera; quaternion; physics |
| glTF 2.0 | Y-up, right-handed, −Z forward | metres (metric, fixed by spec) | seconds | quaternion (native, closest match to canonical) | camera(persp/ortho) · hierarchy(node tree) · timeline(keyframe anim, LINEAR/STEP/CUBICSPLINE) · appearance(PBR) | native z-order (implicit via depth buffer, not authored — matches C6); parametric arrays without vendor extensions; physics (no core-spec engine) |
| IFC (ISO 16739) | Z-up, right-handed, +Y north | metres (metric, project-configurable) | none — static BIM format, no first-class timebase | direction cosines / `Axis2Placement3D` (no Euler, no quaternion) | hierarchy(site/building/storey/space) · appearance(material/surface style) · parametric(profile defs, partial) | **z-order — none exists, IFC is true 3D**; timeline/animation (4D scheduling is external, not geometric); native quaternion (must convert to/from basis vectors) |
| Lottie | 2D, Y-down, origin top-left (AE composition space) | px (device) | seconds | 2D angle around z + skew — single axis | depth(composition stack index) · hierarchy(nested comps/groups) · timeline(keyframes, easing) · appearance | **3D geometry — Lottie is 2D only**; quaternion orientation; camera/perspective; physics |

Ordinal quantities (CV relative depth, z-index rank) never appear in this table as a "native unit" for
any format above — none of these six formats natively emits ordinal-only length. The type carries meaning
only for adapters bridging perception (`code/corpora`-style) sources, which are out of scope for this
table and MUST declare `ordinal` and refuse metric predicates over it (C2).

## 4. The acceptance test

> A scene emitted to two conformant formats must parse back to the same canonical form and therefore
> score **identically** on every predicate the checker evaluates. If two adapters disagree on the score
> for the same canonical scene, **the adapter is wrong — never the checker.**

Procedure: take one canonical document, run it through adapter A's emit → parse round trip and adapter
B's emit → parse round trip, diff the two resulting canonical forms field-by-field (frame-normalized),
then re-run the checker on both. Any score delta is a conformance bug in whichever adapter deviates from
its own declared §1 block.

## 5. Round-trip rules

**Must be lossless** (kernel, §1 SPEC.md):
- Entity identity and semantic type (including the intrinsic-orientation flag that gates `locale`)
- Geometry (all nine primitives) and transform (position, quaternion orientation, scale)
- Anchors, including bound `viewpoint` and `group.transform` (`reflected|rotated|translated`)
- Units — as unit-tagged quantities with a stated conversion factor, never a bare scalar
- Tolerances (`length`, `angle`, `iou`) — dropping these makes every predicate unscoreable
- Temporal order (Allen relations) on any timebase; durations only where the timebase is non-ordinal

**Allowed to be lossy** (advisory, never scored):
- `appearance` (materials, colour, texture) — L1/L2 adapters may drop it entirely
- `physics` internals (engine, solver state) — only `OUTCOME` observables (rest position, contact
  events + their Allen order) must survive; the simulation itself is never round-tripped
- Format-native conveniences with no canonical counterpart (e.g. PPTX slide masters, Tiled tilesets'
  image packing) — these are presentation detail, not kernel claims

An `ordinal` quantity is never "lossy" in the usual sense — it is a **type boundary**: an adapter that
silently promotes an ordinal source to a metric one (fabricating magnitude) fails conformance outright,
regardless of level.

## 6. Format capability matrix

Finer-grained companion to §3: what each format's own schema can actually store. `native` = a named field
exists · `derived` = computable from stored data · `none` = not representable. This is what an adapter
must work around; §3 is the contract it must then declare.

| Concept cluster | SVG | PPTX/OOXML | TMX | glTF 2.0 | IFC | Lottie |
|---|---|---|---|---|---|---|
| Geometry primitives | native | native | native | native | native | native |
| Topology / containment | derived | derived | derived | derived | native (`IfcRel...`) | derived |
| Motion / PATH | none | motion-path anim | none | native anim | none | native anim |
| Temporal / keyframes | none | native (`p:timing`) | tile-anim only | native | none | native |
| Composition SEQ/PAR/ALT | none | native | none | tracks (app-level) | none | precomp (semi) |
| Parametric arrays | `<use>` workaround | none | tileset (partial) | extension-only | native (occurrence) | none |
| Selectors / identity | `id` | shape id | object id/gid | node name (weak) | **GlobalId (strongest)** | layer name/index |
| Camera / projection | none | none | `orientation` (native) | native | presentation-only | none |
| Z-order / paint order | authored (doc order) | authored (XML order) | native (layer stack) | none (render-time) | **none — true 3D** | authored (layer index) |
| Layers visible/hidden | convention only | shape-level | native flag | none | native (`PresentationLayer`) | native (`hd`) |
| Hierarchy / grouping | native `<g>` | native `<grpSp>` | object groups | node children | **richest (spatial structure)** | precomps |
| Chirality / flip | negative-scale | `flipH`/`flipV` | gid flip bits | discouraged | discouraged | negative-scale |
| Snapping / grid | editor-only | editor-only | **native (is a grid)** | none | `IfcGrid` (partial) | none |
| Clip / near-far | `clipPath` (no z) | crop (no z) | none | `znear`/`zfar` (native) | boolean-clip (weak) | masks (no z) |
| Viewport / aspect | `viewBox` (native) | slide size (native) | map dims (native) | none | none | `w`/`h` (native) |
| Physics / rigging *(advisory)* | none | none | none | skins+anim (native) | none | none |

The two `none` cells that matter most: **IFC has no z-order** (it is true 3D — depth is derived from a
camera, exactly as C6 prescribes), and **Lottie has no 3D geometry** (2D only). Neither is a defect; both
are why the profile system exists.
