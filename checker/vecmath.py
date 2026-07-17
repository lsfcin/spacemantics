# Vector and unit-quaternion math in the canonical frame (right-handed, +Z up, +Y forward, +X right).

from __future__ import annotations

import math

Vec3 = tuple[float, float, float]
Quat = tuple[float, float, float, float]  # (w, x, y, z)

IDENTITY: Quat = (1.0, 0.0, 0.0, 0.0)
ZERO: Vec3 = (0.0, 0.0, 0.0)
UP: Vec3 = (0.0, 0.0, 1.0)
FORWARD: Vec3 = (0.0, 1.0, 0.0)
RIGHT: Vec3 = (1.0, 0.0, 0.0)


def add(a: Vec3, b: Vec3) -> Vec3:
    result = (a[0] + b[0], a[1] + b[1], a[2] + b[2])
    return result


def sub(a: Vec3, b: Vec3) -> Vec3:
    result = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    return result


def scaled(a: Vec3, k: float) -> Vec3:
    result = (a[0] * k, a[1] * k, a[2] * k)
    return result


def dot(a: Vec3, b: Vec3) -> float:
    result = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    return result


def cross(a: Vec3, b: Vec3) -> Vec3:
    x = a[1] * b[2] - a[2] * b[1]
    y = a[2] * b[0] - a[0] * b[2]
    z = a[0] * b[1] - a[1] * b[0]
    return (x, y, z)


def length(a: Vec3) -> float:
    squared = dot(a, a)
    result = math.sqrt(squared)
    return result


def normalize(a: Vec3) -> Vec3:
    size = length(a)
    if size == 0.0:
        raise ValueError("cannot normalize a zero vector")
    result = scaled(a, 1.0 / size)
    return result


def lerp(a: Vec3, b: Vec3, u: float) -> Vec3:
    delta = sub(b, a)
    step = scaled(delta, u)
    result = add(a, step)
    return result


def quat_normalize(q: Quat) -> Quat:
    size = math.sqrt(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2)
    if size == 0.0:
        raise ValueError("cannot normalize a zero quaternion")
    result = (q[0] / size, q[1] / size, q[2] / size, q[3] / size)
    return result


def rotate(q: Quat, v: Vec3) -> Vec3:
    """Rotate v by the unit quaternion q (Rodrigues form; no Euler ever — C4)."""
    unit = quat_normalize(q)
    w = unit[0]
    axis = (unit[1], unit[2], unit[3])
    t = cross(axis, v)
    t = scaled(t, 2.0)
    wt = scaled(t, w)
    at = cross(axis, t)
    partial = add(v, wt)
    result = add(partial, at)
    return result


def basis_of(q: Quat) -> tuple[Vec3, Vec3, Vec3]:
    """The object's own (right, forward, up) axes, i.e. its columns in canonical coordinates."""
    right = rotate(q, RIGHT)
    forward = rotate(q, FORWARD)
    up = rotate(q, UP)
    return (right, forward, up)


def angle_between(a: Vec3, b: Vec3) -> float:
    """Unsigned angle in radians."""
    ua = normalize(a)
    ub = normalize(b)
    raw = dot(ua, ub)
    clamped = max(-1.0, min(1.0, raw))
    result = math.acos(clamped)
    return result
