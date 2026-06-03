import sys
try:
    import imp
except ImportError:
    import importlib
    sys.modules['imp'] = importlib

import math
import pygame
import pymunk as pm

# MODULARIZAÇÃO: Centralização de constantes e funções utilitárias

class GameConfig:
    # Dimensões da janela
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 650
    
    # Física
    # SM 10: Ajuste de gravidade
    GRAVITY = (0.0, -750.0) 
    BIRD_RADIUS = 12
    PIG_RADIUS = 14
    BIRD_COLLISION_TYPE = 0
    PIG_COLLISION_TYPE = 1
    WOOD_COLLISION_TYPE = 2
    
    # Sling configuration
    SLING_X = 135
    SLING_Y = 450
    SLING2_X = 160
    SLING2_Y = 450
    ROPE_LENGTH = 90
    BIGGER_ROPE = 102
    
    # Cores
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    PANEL_BG = (35, 18, 8)
    PANEL_BORDER = (210, 165, 30)
    BUTTON_NORMAL = (170, 60, 20)
    BUTTON_HOVER = (210, 90, 35)
    BUTTON_BORDER_COLOR = (210, 165, 30)

def to_pygame(p):
    """Converter coordenadas pymunk para pygame"""
    return int(p.x), int(-p.y + 600)

def vector(p0, p1):
    """Retorne o vetor dos pontos."""
    return (p1[0] - p0[0], p1[1] - p0[1])

def unit_vector(v):
    """Retorne o vetor unitário dos pontos."""
    h = math.hypot(v[0], v[1])
    if h == 0:
        h = 1e-15
    return (v[0] / h, v[1] / h)

def distance(xo, yo, x, y):
    """Calcula a distância entre dois pontos."""
    return math.dist((xo, yo), (x, y))
