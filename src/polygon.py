from typing import Tuple
import pymunk as pm
from pymunk import Vec2d
import pygame
import math


def _load_sprite(image_path: str, rect_coords: Tuple[int, int, int, int]) -> pygame.Surface:
    """Helper function to load and crop sprite images"""
    image = pygame.image.load(image_path).convert_alpha()
    rect = pygame.Rect(*rect_coords)
    return image.subsurface(rect).copy()


class Polygon:
    def __init__(self, pos: Tuple[float, float], length: float, height: float, space: pm.Space, mass: float = 5.0) -> None:
        moment: float = 1000
        body: pm.Body = pm.Body(mass, moment)
        body.position = Vec2d(*pos)
        shape: pm.Poly = pm.Poly.create_box(body, (length, height))
        shape.color = (0, 0, 255)
        shape.friction = 0.5
        shape.collision_type = 2
        space.add(body, shape)
        self.body: pm.Body = body
        self.shape: pm.Poly = shape
        self.beam_image: pygame.Surface = _load_sprite("../resources/images/wood.png", (251, 357, 86, 22))
        self.column_image: pygame.Surface = _load_sprite("../resources/images/wood2.png", (16, 252, 22, 84))

    def to_pygame(self, p):
        """Convert pymunk to pygame coordinates"""
        return int(p.x), int(-p.y+600)

    def draw_poly(self, element, screen):
        """Draw beams and columns"""
        poly = self.shape
        ps = poly.get_vertices()
        ps.append(ps[0])
        ps = map(self.to_pygame, ps)
        ps = list(ps)
        color = (255, 0, 0)
        pygame.draw.lines(screen, color, False, ps)
        if element == 'beams':
            p = poly.body.position
            p = Vec2d(*self.to_pygame(p))
            angle_degrees = math.degrees(poly.body.angle) + 180
            rotated_logo_img = pygame.transform.rotate(self.beam_image,
                                                       angle_degrees)
            offset = Vec2d(*rotated_logo_img.get_size()) / 2.
            p = p - offset
            np = p
            screen.blit(rotated_logo_img, (np.x, np.y))
        if element == 'columns':
            p = poly.body.position
            p = Vec2d(*self.to_pygame(p))
            angle_degrees = math.degrees(poly.body.angle) + 180
            rotated_logo_img = pygame.transform.rotate(self.column_image,
                                                       angle_degrees)
            offset = Vec2d(*rotated_logo_img.get_size()) / 2.
            p = p - offset
            np = p
            screen.blit(rotated_logo_img, (np.x, np.y))
