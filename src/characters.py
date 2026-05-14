from typing import Tuple
import pymunk as pm
from pymunk import Vec2d, Body, Circle, Space

BIRD_POWER_MULTIPLIER = 53
BIRD_COLLISION_TYPE = 0
PIG_COLLISION_TYPE = 1
SHAPE_ELASTICITY = 0.95
SHAPE_FRICTION = 1.0


class Bird:
    def __init__(self, distance: float, angle: float, x: float, y: float, space: Space) -> None:
        self.life: int = 20
        mass: float = 5
        radius: float = 12
        inertia: float = pm.moment_for_circle(mass, 0, radius, (0, 0))
        body: Body = pm.Body(mass, inertia)
        body.position = x, y
        power: float = distance * BIRD_POWER_MULTIPLIER
        impulse: Vec2d = power * Vec2d(1, 0)
        angle = -angle
        body.apply_impulse_at_local_point(impulse.rotated(angle))
        shape: Circle = pm.Circle(body, radius, (0, 0))
        shape.elasticity = SHAPE_ELASTICITY
        shape.friction = SHAPE_FRICTION
        shape.collision_type = BIRD_COLLISION_TYPE
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
        shape.elasticity = SHAPE_ELASTICITY
        shape.friction = SHAPE_FRICTION
        shape.collision_type = PIG_COLLISION_TYPE
        space.add(body, shape)
        self.body: Body = body
        self.shape: Circle = shape
