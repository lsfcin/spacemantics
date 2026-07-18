# Score a model's placement: build a texpace document from the task + the model's poses, then run the checker.

from __future__ import annotations

from dataclasses import dataclass

from checker import PASS, CheckReport, check_scene, scene_from

CANONICAL_FRAME = {"handedness": "right", "up": "+Z", "forward": "+Y", "origin": "datum"}
IDENTITY = [1.0, 0.0, 0.0, 0.0]


@dataclass(frozen=True)
class ScoreResult:
    passed: int
    scored: int
    solved: bool
    report: CheckReport

    def fraction(self) -> float:
        result = 0.0 if self.scored == 0 else self.passed / self.scored
        return result


def build_document(task: dict, header: dict, poses: dict) -> dict:
    """Merge fixed anchors with the model's poses into one scene document the checker can load."""
    entities = []
    for spec in task["entities"]:
        entity = _entity(spec, poses)
        entities.append(entity)
    document = {
        "texpace": "1.0",
        "profile": header["profile"],
        "frame": CANONICAL_FRAME,
        "units": {"length": "m", "angle": "rad"},
        "timebase": header["timebase"],
        "tolerance": header["tolerance"],
        "entities": entities,
        "viewpoints": task.get("viewpoints", []),
        "claims": task["claims"],
    }
    return document


def _entity(spec: dict, poses: dict) -> dict:
    name = spec["name"]
    entity = {"name": name, "type": spec["type"], "shape": spec["shape"]}
    if spec.get("fixed"):
        entity["position"] = spec["position"]
        entity["orientation"] = spec.get("orientation", IDENTITY)
    else:
        pose = poses.get(name, {})
        entity["position"] = pose.get("position", [0.0, 0.0, 0.0])
        entity["orientation"] = pose.get("orientation", IDENTITY)
    return entity


def score_poses(task: dict, header: dict, poses: dict) -> ScoreResult:
    """The scorer both arms share. `solved` = every scored claim passed (no FAIL, no ERROR)."""
    document = build_document(task, header, poses)
    scene = scene_from(document)
    report = check_scene(scene)
    scored_verdicts = report.scored()
    total = len(scored_verdicts)
    passed = sum(1 for verdict in scored_verdicts if verdict.status == PASS)
    solved = report.passed() and total > 0
    result = ScoreResult(passed=passed, scored=total, solved=solved, report=report)
    return result
