from typing import Tuple
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Space


class Bird:
    def __init__(self, distance: float, angle: float, x: float, y: float, space: Space) -> None:
        self.life: int = 20
        mass: float = 5
        radius: float = 12
        inertia: float = pm.moment_for_circle(mass, 0, radius, (0, 0))
        body: Body = pm.Body(mass, inertia)
        body.position = x, y
        power: float = distance * 53
        impulse: Vec2d = power * Vec2d(1, 0)
        angle = -angle
        body.apply_impulse_at_local_point(impulse.rotated(angle))
        shape: Circle = pm.Circle(body, radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = 0
        space.add(body, shape)
        self.body: Body = body
        self.shape: Circle = shape


class Pig:
    def __init__(self, x: float, y: float, space: Space) -> None:
        self.life: int = 20
        mass: float = 5
        radius: float = 14
        inertia: float = pm.moment_for_circle(mass, 0, radius, (0, 0))
        body: Body = pm.Body(mass, inertia)
        body.position = x, y
        shape: Circle = pm.Circle(body, radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 1
        shape.collision_type = 1
        space.add(body, shape)
        self.body: Body = body
        self.shape: Circle = shape
