# texpace — Benchmark Families Detail
> Per-family task specs: format rationale, spatial concepts exercised, literature anchor, and one concrete L1/L2/L3 example each

Parent: [TAXONOMY.md](TAXONOMY.md) — principles, level definitions, conditions, metrics, threats to
validity. All examples below are illustrative specs, not generator output; actual ground truth is
produced by a parametric generator per family (TAXONOMY.md §1).

### 1. 2D graph/diagram drawing (SVG) — calibration family
- **Concepts:** planar-graph topology (RCC-8 `DC`/`EC` for crossing-free adjacency), node placement, edge
  crossing count, degree constraints.
- **Anchor:** PlanarBench, GeoGramBench — report numbers directly comparable to their published results.
- **L1:** 3 nodes, 2 edges, `world` anchor, "connect A–B and B–C; no edges cross."
- **L2:** 6-8 node planar graph, layer grouping, moderate constraint depth (adjacency + layer + spacing).
- **L3:** dense graph, negation ("no two edges cross"), quantification ("every node has degree ≤3"), tight
  orthogonal-grid alignment tolerance.

### 2. 2D vector diagram (SVG)
- **Concepts:** `DIR`/`DIST`/`TOP` between shapes, alignment, containment (`TPP`/`NTPP`), path composition.
- **Anchor:** SVGenius, GeoSVG-RL.
- **L1:** 3 shapes, `world` anchor, "circle above square, both left of triangle."
- **L2:** nested groups, containment, alignment constraints (align-left, equal-spacing).
- **L3:** tight-tolerance nesting, negation ("no shape overlaps the label"), quantification ("each icon has
  exactly one label").

### 3. 2D UI layout (SVG)
- **Concepts:** Cassowary linear constraints, `DIST` spacing, parent-child containment, z-order of
  overlapping widgets.
- **Anchor:** LLMs-as-Layout-Designers, Cassowary constraint solving.
- **L1:** 3 widgets in one row, `world` anchor, unambiguous spacing.
- **L2:** multi-panel layout, nested containers, `locale` anchors (relative to the container's own frame),
  align + equal-width chains.
- **L3:** conflicting constraint resolution under tight tolerance, negation ("no widget overlaps
  another"), quantification ("every toolbar button is equally spaced").

### 4. 2D slides (PPTX)
- **Concepts:** content-aware placement of text/image boxes, rotation derived from shear/scale (per
  `dsl/CONFLICTS.md` C4), grouping, z-order.
- **Anchor:** content-aware layout literature.
- **L1:** 3 elements, `world` anchor, "title above image, both above caption."
- **L2:** multi-slide deck consistency, group transforms, `locale`-anchored relation chains.
- **L3:** dense slide with rotated elements, negation ("no text box overlaps the image"), quantification
  ("every bullet aligned to the same left margin").

### 5. 2.5D technical/engineering (SVG + declared iso projection) — novel
- **Concepts:** declared camera/projection module (`depth = dot(position, view_dir)`, per CONFLICTS C6),
  isometric/dimetric drawing convention, `DIR` under an iso projection.
- **Anchor:** novel — no direct published baseline.
- **L1:** 3 primitives under a declared NE dimetric camera, `world` anchor, unambiguous depth order.
- **L2:** part assembly with moderate occlusion, mixed `world`/`locale` anchors, layer tie-break.
- **L3:** occlusion cycles, tight depth-tie tolerance, negation ("no part occludes the label"), mid-scene
  camera reassignment (exercises "camera ≠ entity orientation," CONFLICTS C4 corollary).

### 6. 2.5D gaming (Tiled TMX) — novel, isoroll dogfood
- **Concepts:** grid/voxel units (CONFLICTS C2), derived depth key `(row−col+elev)·10000+band` under an NE
  camera, layer tie-break, `TOP` tile adjacency, chirality rule (rotation = cell remapping, never
  mirroring).
- **Anchor:** novel — depth/occlusion under isoroll's real conventions.
- **L1:** 3×3 tile map, few tokens, `world` anchor, "token A occludes token B."
- **L2:** multi-layer map (floor/walls/tokens), moderate elevation change, occlusion chains.
- **L3:** depth-cycle map (isoroll's `swapSide` bug class), negation ("no token behind a wall it is
  supposedly in front of"), chirality/rotation stress test.

### 7. 3D generic modeling (glTF) — credibility anchor
- **Concepts:** full `DIR`/`DIST`/`TOP`/`PATH` in 3D, `world`/`locale`/`group` anchors, canonical Z-up
  right-handed frame, quaternion rotation.
- **Anchor:** SceneCraft / SpatialGrammar / HDSL — head-to-head, reusing **their** metrics (DRFR, collision
  rate, constraint-pass rate, CLIP).
- **L1:** 3-5 objects, `world` anchor, zero collisions — mirrors their simplest published setting.
- **L2:** room-scale scene (~10-15 objects), mixed anchors, moderate constraint chains — the
  published-benchmark composition level.
- **L3:** dense scene, `group` anchor with explicit `viewpoint_transform`, negation (no collisions among N
  objects), quantification, tight collision tolerance — scored on DRFR + collision-rate +
  constraint-pass-rate + CLIP exactly as published.

### 8. 3D IFC/BIM (IFC) — novel
- **Concepts:** canonical spatial-array module (CONFLICTS C5), per-instance overrides, storeys (Z-up
  frame), quantity takeoff, SI-canonical metric units.
- **Anchor:** novel — parametric repetition, storeys, quantities.
- **L1:** single building module, `world` anchor, "wall north of door," no array.
- **L2:** 3-4× repeated linear module array, one storey, moderate quantity assertions ("4 windows per
  unit").
- **L3:** casinhas-grounded 7× parametric array with a distinct corner-unit override (CONFLICTS C5
  example), multi-storey, quantification over the whole array ("every unit but the corner has identical
  footprint"), tight dimensional tolerance.

### 9. 2D + time, kinematic (Lottie)
- **Concepts:** `PATH`, Allen interval relations, canonical `seconds` timebase (CONFLICTS C3), `SEQ`/
  `PAR`/`ALT` composition, dynamics as an orthogonal execution layer.
- **Anchor:** PRISM.
- **L1:** one object moves along a straight path, `world` anchor, one Allen relation ("A moves before B
  appears").
- **L2:** 2-3 objects with `SEQ`/`PAR` composition, moderate path-shape variety (through/across).
- **L3:** dense timeline, quantified `HOLD` ("maintain contact for ≥2s"), negation ("A never overlaps B
  during the clip"), tight timing tolerance.

### 10. 2D + time, physics, outcome-checked (Lottie + engine) — novel
- **Concepts:** outcome-checking (state initial conditions + goal post-conditions; a recognized engine
  simulates; the checker verifies only observables — rest positions, contact events, Allen ordering),
  Talmy force dynamics (`TOP` + force flag).
- **Anchor:** PRISM + novel (outcome-checked physics is texpace's own contribution).
- **L1:** one ball dropped, `world` anchor, one observable ("ball rests on floor by t=2s").
- **L2:** 2-3 body collision scene, moderate observable set (contact events + final resting `TOP`
  relations).
- **L3:** multi-body scene, tight rest-position tolerance, negation ("no two bodies interpenetrate at
  rest"), ordered contact-event constraints (Allen), engine-agnostic scoring.

### 11. 3D + time incl. rigging (glTF animation) — novel
- **Concepts:** skinning/rigging, quaternion keyframe interpolation, `PATH` in 3D over time, `locale`
  anchor on articulated parts (requires an oriented relatum).
- **Anchor:** novel — no published 3D+rigging DSL+checker baseline.
- **L1:** one rigged object, one clip, `world` anchor, "arm rises above shoulder by t=1s."
- **L2:** 2 rigged characters, moderate interaction (facing change via `locale` anchor), `SEQ` composition
  of clips.
- **L3:** multi-joint rig, `group` anchor with bound viewpoint ("A faces B as seen from camera"),
  quantified joint-limit constraints, tight timing + pose tolerance.

### 12. Cross-view / multi-viewpoint consistency (glTF / SVG)
- **Concepts:** `group` anchor (ternary: fig, gnd, viewpoint), `viewpoint_transform ∈ {reflected, rotated,
  translated}`, the **arity gate** (`group` without a bound viewpoint → reject), cross-view consistency.
- **Anchor:** COMFORT — directly exercises the arity gate that is texpace's core anchor-model claim.
- **L1:** one `group` statement, one bound viewpoint, "as seen from V, A is left of B."
- **L2:** same scene evaluated under 2-3 viewpoints, transform-consistent verdicts required, one planted
  arity-gate violation as a distractor.
- **L3:** the same relation under `reflected` vs `rotated` vs `translated` transforms disagreeing by
  design, quantification across viewpoints ("under every declared viewpoint, A is left of B"), tight
  consistency tolerance, multiple planted arity-gate violations.

### 13. Convention reconciliation / dogfood (cross-format) — novel
- **Concepts:** all six `dsl/CONFLICTS.md` conventions (frame, units, time base, rotation, repetition,
  depth) exercised in one scene; the cross-format consistency test (one scene → SVG + glTF → parse back →
  identical checker verdict).
- **Anchor:** novel — this is the family that would fix isoroll's three conflicting depth conventions.
- **L1:** one scene emitted to 2 formats (SVG + glTF), `world` anchor, verify identical checker verdict on
  one relation.
- **L2:** an isoroll-grounded dogfood scene emitted to TMX + SVG, moderate relation set, verify the
  canonical depth-derivation matches both isoroll's historical NE and SE formulas under the correctly
  declared camera.
- **L3:** the casinhas module as a 7× parametric array (ROADMAP verification checklist) emitted to IFC +
  glTF, an ordinal-typed CV depth value injected as a planted type-error, tight cross-format tolerance,
  full six-conflict coverage in one scene.
