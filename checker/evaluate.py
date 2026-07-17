# Claim evaluation: dispatch one claim to its predicate, with the quantifiers and the temporal wrapper around it.

from __future__ import annotations

from itertools import combinations

from . import allen, direction, metrics, rcc8
from .report import ERROR, FAIL, PASS, SKIPPED, CheckReport, Verdict
from .scene import Scene
from .units import Quantity, UnitTypeError

QUANTIFIERS: frozenset[str] = frozenset({"none", "every"})


def check_scene(scene: Scene) -> CheckReport:
    """Score every claim against the FINAL state (or the stated instant). Actions are the program; claims are the spec."""
    report = CheckReport(free_dofs=_free_dofs(scene))
    for claim in scene.claims:
        verdict = _verdict_for(scene, claim)
        report.add(verdict)
    return report


def _free_dofs(scene: Scene) -> tuple[str, ...]:
    free = []
    for name, entity in scene.entities.items():
        for dof in sorted(entity.free):
            free.append(f"{name}.{dof}")
    return tuple(free)


def _verdict_for(scene: Scene, claim: dict) -> Verdict:
    mode = claim.get("mode", "assert")
    text = claim.get("text", _render(claim))
    try:
        held, detail = _evaluate(scene, claim)
    except (UnitTypeError, direction.AnchorError, metrics.PredicateError) as failure:
        return Verdict(ERROR, mode, text, str(failure))
    except KeyError as failure:
        return Verdict(ERROR, mode, text, f"malformed claim: missing {failure}")
    if held is None:
        return Verdict(SKIPPED, mode, text, detail)
    status = PASS if held else FAIL
    return Verdict(status, mode, text, detail)


def _evaluate(scene: Scene, claim: dict) -> tuple[bool | None, str]:
    if "quant" in claim:
        result = _quantified(scene, claim)
        return result
    if claim.get("pred") == "HOLD":
        result = _hold(scene, claim)
        return result
    t = float(claim.get("at", 0.0))
    result = _atomic(scene, claim, t)
    return result


def _atomic(scene: Scene, claim: dict, t: float) -> tuple[bool | None, str]:
    predicate = claim["pred"]
    if predicate == "TOP":
        region_a = scene.region_of(claim["a"], t)
        region_b = scene.region_of(claim["b"], t)
        expected = tuple(claim["rcc"])
        held, found = rcc8.holds(region_a, region_b, expected, scene.tolerance.length)
        return (held, f"rcc8={found}, expected {'|'.join(expected)}")
    if predicate == "DIR":
        anchor = claim.get("anchor", {"kind": "world"})
        result = direction.holds(scene, claim["fig"], claim["gnd"], claim["term"], anchor, t)
        return result
    if predicate == "DIST":
        quantity = Quantity(float(claim["q"]["value"]), claim["q"]["unit"])
        result = metrics.distance_holds(scene, claim["fig"], claim["gnd"], claim["op"], quantity, t)
        return result
    if predicate == "FACES":
        result = metrics.faces(scene, claim["a"], claim["b"], t)
        return result
    if predicate == "PARALLEL":
        result = metrics.axis_angle_holds(scene, claim["a"], claim["b"], 0.0, t)
        return result
    if predicate == "PERPENDICULAR":
        result = metrics.axis_angle_holds(scene, claim["a"], claim["b"], 90.0, t)
        return result
    if predicate == "ALIGNED":
        axis = claim.get("axis", "x")
        result = metrics.aligned(scene, claim["a"], claim["b"], axis, t)
        return result
    if predicate == "COUNT":
        result = _count(scene, claim)
        return result
    if predicate == "ALLEN":
        result = _allen(scene, claim)
        return result
    raise metrics.PredicateError(f"unknown predicate '{predicate}'")


def _count(scene: Scene, claim: dict) -> tuple[bool, str]:
    """Coverage. Without it a model 'solves' a scene by deleting the objects that were in the way."""
    names = scene.select(claim["set"])
    found = len(names)
    wanted = int(claim["n"])
    op = claim.get("op", "==")
    held = metrics.compare(float(found), op, float(wanted), 0.0)
    return (held, f"count={found} {op} {wanted}")


def _allen(scene: Scene, claim: dict) -> tuple[bool, str]:
    """Allen relations between declared event intervals. Order only, if the timebase is ordinal (C3)."""
    events = scene.events
    first = events[claim["a"]]
    second = events[claim["b"]]
    eps = scene.tolerance.time
    found = allen.relation(first, second, eps)
    held = allen.holds(first, second, claim["rel"], eps)
    return (held, f"allen={found}, expected {claim['rel']}")


def _hold(scene: Scene, claim: dict) -> tuple[bool, str]:
    """HOLD(pred, interval): sampled invariance. On an ordinal timebase durations do not exist — type error (C3)."""
    if scene.is_ordinal_timebase():
        raise UnitTypeError(
            "timebase is ordinal ('steps'): durations do not exist, so 'hold ... for <duration>' is a type error (C3)"
        )
    start, end = claim["interval"]
    samples = int(claim.get("samples", 16))
    inner = claim["claim"]
    span = float(end) - float(start)
    for index in range(samples + 1):
        t = float(start) + span * index / samples
        held, detail = _atomic(scene, inner, t)
        if not held:
            return (False, f"broke at t={t:.3f}s: {detail}")
    return (True, f"held over [{start}s, {end}s] at {samples + 1} samples")


def _quantified(scene: Scene, claim: dict) -> tuple[bool, str]:
    quantifier = claim["quant"]
    if quantifier not in QUANTIFIERS:
        raise metrics.PredicateError(f"unknown quantifier '{quantifier}'")
    inner = claim["pred"]
    t = float(claim.get("at", 0.0))
    bindings = _bindings(scene, claim["over"])
    witnesses = []
    for bound in bindings:
        merged = dict(inner)
        merged.update(bound)
        held, detail = _atomic(scene, merged, t)
        if quantifier == "none" and held:
            names = list(bound.values())
            return (False, f"witness: {names} — {detail}")
        if quantifier == "every" and not held:
            names = list(bound.values())
            return (False, f"counterexample: {names} — {detail}")
        witnesses.append(bound)
    return (True, f"{quantifier} holds over {len(witnesses)} binding(s)")


def _bindings(scene: Scene, over: dict) -> list[dict]:
    """'pairs' binds a,b over unordered pairs (the 'no two overlap' idiom); 'set' binds one variable."""
    if "pairs" in over:
        names = scene.select(over["pairs"])
        pairs = combinations(names, 2)
        result = [{"a": a, "b": b} for a, b in pairs]
        return result
    names = scene.select(over["set"])
    variable = over.get("as", "a")
    result = [{variable: name} for name in names]
    return result


def _render(claim: dict) -> str:
    parts = [f"{key}={value}" for key, value in claim.items() if key != "text"]
    joined = " ".join(parts)
    return joined
