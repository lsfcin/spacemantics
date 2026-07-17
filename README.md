# Spacemantics
> Give LLM agents spatial/visual capability through a verifiable spatial DSL — not pixels, not vibes.

## What it does

LLMs are weak at spatial/visual construction (positioning, layers, viewpoints, occlusion, 2D/2.5D/3D/4D
coordinates). Spacemantics closes the gap with three parts:

- **DSL** — a small textual grammar that carries position, size, layer/z, facing/viewpoint, spatial
  relations ("in front of", "left of", "on top of", "occludes"), and temporal keyframes/trajectories.
  One grammar, four profiles: 2D · 2.5D-iso · 3D · 4D-time.
- **Checker** — deterministic verifier that owns geometric truth: parses DSL → geometry → scores
  relation satisfaction, coordinate error, z-order, cross-view consistency, silhouette IoU, and
  temporal order. The model's eyes never assert geometry; code does.
- **Benchmark** — cross-dimensional, cross-model, ablated harness measuring the capability lift
  (free-text → DSL → +skill → +checker feedback) across Claude models and opencode models.

Optional **perception** thread: classic CV (segmentation, depth, detection, tracking) as a
visuals→semantics bridge to score rendered/real images when synthetic ground truth is unavailable.

## Try the checker

```bash
python -m checker examples/office.json     # scores 10 claims; catches 2 deliberate type/arity errors
python -m pytest tests                      # 39 cases, all green
```

The checker owns geometric truth. It scores a scene's **claims** — RCC-8 topology, Rectangle-Algebra
direction under three anchors, Allen time, numeric distance/orientation — on definite scenes in O(n²), with
an explicit tolerance on every predicate. A claim that cannot be evaluated as written (an ordinal quantity
in a metric predicate; a projective term with no readable frame) is an **ERROR**, never a silent FAIL.

## Status
**M1 in progress.** Thin kernel + checker built and green (`checker/`, 39 tests). The concept-by-concept
checkability filter has been run — see [dsl/CHECKABILITY.md](dsl/CHECKABILITY.md); four `core` concepts were
demoted for lacking a working predicate. Surface v2 docs partly regenerated (TYPES + SPEC done; EXAMPLES +
grammar pending). Full plan → [ROADMAP.md](ROADMAP.md).

## License
MIT

---
[CONTEXT.md](CONTEXT.md) · [ROADMAP.md](ROADMAP.md)
