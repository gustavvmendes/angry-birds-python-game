from typing import Tuple
import os
import pymunk as pm
from pymunk import Vec2d
import pygame
import math

_IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resources', 'images')
ORIENTATION_ADJUSTMENT = 180


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
        self.beam_image: pygame.Surface = _load_sprite(os.path.join(_IMAGES_DIR, "wood.png"), (251, 357, 86, 22))
        self.column_image: pygame.Surface = _load_sprite(os.path.join(_IMAGES_DIR, "wood2.png"), (16, 252, 22, 84))

    def to_pygame(self, p):
        """Convert pymunk to pygame coordinates"""
        return int(p.x), int(-p.y+600)

    def _render_sprite(self, image: pygame.Surface, poly: pm.Poly, screen: pygame.Surface) -> None:
        """Render a rotated sprite centered on the polygon body position"""
        p = Vec2d(*self.to_pygame(poly.body.position))
        angle_degrees = math.degrees(poly.body.angle) + ORIENTATION_ADJUSTMENT
        rotated_img = pygame.transform.rotate(image, angle_degrees)
        p = p - Vec2d(*rotated_img.get_size()) / 2.
        screen.blit(rotated_img, (p.x, p.y))

    def draw_poly(self, element, screen):
        """Draw beams and columns"""
        poly = self.shape
        ps = poly.get_vertices()
        ps.append(ps[0])
        ps = list(map(self.to_pygame, ps))
        pygame.draw.lines(screen, (255, 0, 0), False, ps)
        if element == 'beams':
            self._render_sprite(self.beam_image, poly, screen)
        elif element == 'columns':
            self._render_sprite(self.column_image, poly, screen)
