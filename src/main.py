import sys
import os
import math
import time
import pygame

# MODULARIZAÇÃO: Importando utilitários e configurações
from utils import GameConfig, to_pygame, vector, unit_vector, distance

# Truque para Python 3.13 (redundante mas seguro)
try:
    import imp
except ImportError:
    import importlib
    sys.modules['imp'] = importlib

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(_SRC_DIR, '..', 'resources', 'images')
SOUNDS_DIR = os.path.join(_SRC_DIR, '..', 'resources', 'sounds')
import pymunk as pm
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False
from characters import Bird
from level import Level
from screen_manager import ScreenManager

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
redbird = pygame.image.load(os.path.join(IMAGES_DIR, "red-bird3.png")).convert_alpha()
background2 = pygame.image.load(os.path.join(IMAGES_DIR, "background3.png")).convert_alpha()
sling_image = pygame.image.load(os.path.join(IMAGES_DIR, "sling-3.png")).convert_alpha()
full_sprite = pygame.image.load(os.path.join(IMAGES_DIR, "full-sprite.png")).convert_alpha()
rect = pygame.Rect(181, 1050, 50, 50)
cropped = full_sprite.subsurface(rect).copy()
pig_image = pygame.transform.scale(cropped, (30, 30))
buttons = pygame.image.load(os.path.join(IMAGES_DIR, "selected-buttons.png")).convert_alpha()
pig_happy = pygame.image.load(os.path.join(IMAGES_DIR, "pig_failed.png")).convert_alpha()
stars = pygame.image.load(os.path.join(IMAGES_DIR, "stars-edited.png")).convert_alpha()

star1 = stars.subsurface(pygame.Rect(0, 0, 200, 200)).copy()
star2 = stars.subsurface(pygame.Rect(204, 0, 200, 200)).copy()
star3 = stars.subsurface(pygame.Rect(426, 0, 200, 200)).copy()
pause_button = buttons.subsurface(pygame.Rect(164, 10, 60, 60)).copy()
replay_button = buttons.subsurface(pygame.Rect(24, 4, 100, 100)).copy()
next_button = buttons.subsurface(pygame.Rect(142, 365, 130, 100)).copy()
play_button = buttons.subsurface(pygame.Rect(18, 212, 100, 100)).copy()

clock = pygame.time.Clock()
running = True
space = pm.Space()
# SM 10: Gravidade
space.gravity = GameConfig.GRAVITY
space.damping = 0.5

pigs, birds, columns, beams, bird_path = [], [], [], [], []
mouse_pressed = False
t1, t2, counter, score, game_state = 0, 0, 0, 0, 0
screen_manager = ScreenManager()
bonus_score_once, wall = True, False
bold_font = pygame.font.SysFont("arial", 30, bold=True)
bold_font2 = pygame.font.SysFont("arial", 40, bold=True)
bold_font3 = pygame.font.SysFont("arial", 50, bold=True)
label_font = pygame.font.SysFont("arial", 22, bold=True)

# Static floor
static_body = pm.Body(body_type=pm.Body.STATIC)
static_lines = [pm.Segment(static_body, (0.0, 060.0), (1200.0, 060.0), 0.0)]
for line in static_lines:

    line.elasticity = 0.0
    line.friction = 10.0
    line.collision_type = 3
space.add(static_body)
for line in static_lines:
    space.add(line)

def load_music():
    song1 = os.path.join(SOUNDS_DIR, 'angry-birds.ogg')
    pygame.mixer.music.load(song1)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def is_mouse_on_slingshot(x, y):
    return (100 < x < 250) and (370 < y < 550)

def sling_action():
    global mouse_distance, angle, x_mouse, y_mouse
    mouse_distance = distance(GameConfig.SLING_X, GameConfig.SLING_Y, x_mouse, y_mouse)
    if mouse_distance > GameConfig.ROPE_LENGTH:
        mouse_distance = GameConfig.ROPE_LENGTH
    v = vector((GameConfig.SLING_X, GameConfig.SLING_Y), (x_mouse, y_mouse))
    uv1, uv2 = unit_vector(v)
    pu = (uv1 * mouse_distance + GameConfig.SLING_X, uv2 * mouse_distance + GameConfig.SLING_Y)
    pygame.draw.line(screen, GameConfig.BLACK, (GameConfig.SLING2_X, GameConfig.SLING2_Y), pu, 5)
    screen.blit(redbird, (pu[0] - 20, pu[1] - 20))
    pygame.draw.line(screen, GameConfig.BLACK, (GameConfig.SLING_X, GameConfig.SLING_Y), pu, 5)
    dy, dx = y_mouse - GameConfig.SLING_Y, x_mouse - GameConfig.SLING_X
    angle = math.atan(dy / (dx if dx != 0 else 1e-15))

def draw_ui_panel():
    overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
    overlay.set_alpha(165); overlay.fill(GameConfig.BLACK)
    screen.blit(overlay, (0, 0))
    panel = pygame.Rect(300, 55, 600, 560)
    pygame.draw.rect(screen, GameConfig.PANEL_BG, panel, border_radius=20)
    pygame.draw.rect(screen, GameConfig.PANEL_BORDER, panel, 5, border_radius=20)

def draw_level_cleared():
    global game_state, bonus_score_once, score
    if level.number_of_birds < 0 or len(pigs) != 0: return
    if bonus_score_once:
        score += (level.number_of_birds - 1) * 10000
        bonus_score_once = False
    screen_manager.change(4); draw_ui_panel()
    title = bold_font3.render("Level Cleared!", 1, GameConfig.WHITE)
    screen.blit(title, (430, 80))
    if score >= level.one_star: screen.blit(star1, (310, 190))
    if score >= level.two_star: screen.blit(star2, (500, 170))
    if score >= level.three_star: screen.blit(star3, (700, 200))
    score_text = bold_font2.render(str(score), 1, GameConfig.WHITE)
    screen.blit(score_text, (550, 400))
    draw_interactive_button(510, 475, 120, 120, (510<=x_mouse<=610 and 475<=y_mouse<=575), replay_button, "REPLAY", 10)
    draw_interactive_button(625, 475, 150, 120, (625<=x_mouse<=755 and 475<=y_mouse<=575), next_button, "NEXT", 40)

def draw_level_failed():
    global game_state
    if level.number_of_birds <= 0 and time.time() - t2 > 5 and len(pigs) > 0:
        screen_manager.change(3); draw_ui_panel()
        # SM 05: GAME OVER
        title = bold_font3.render("GAME OVER", 1, GameConfig.RED)
        screen.blit(title, (450, 90))
        screen.blit(pig_happy, (380, 145))
        draw_interactive_button(550, 455, 120, 120, (550<=x_mouse<=670 and 455<=y_mouse<=575), replay_button, "RETRY", 10)

def draw_interactive_button(bx, by, w, h, hover, img, label, off_x):
    bc = GameConfig.BUTTON_HOVER if hover else GameConfig.BUTTON_NORMAL
    rr = pygame.Rect(bx - 10, by - 10, w, h)
    pygame.draw.rect(screen, bc, rr, border_radius=18)
    pygame.draw.rect(screen, GameConfig.BUTTON_BORDER_COLOR, rr, 3, border_radius=18)
    screen.blit(img, (bx, by))
    lbl = label_font.render(label, 1, GameConfig.WHITE)
    screen.blit(lbl, (bx + off_x, by + 103))

def restart():
    for obj_list in [pigs, birds, columns, beams]:
        for obj in list(obj_list):
            space.remove(obj.shape, obj.shape.body)
            obj_list.remove(obj)

def post_solve_bird_pig(arbiter, space, _):
    a, b = arbiter.shapes
    p2 = to_pygame(b.body.position)
    pygame.draw.circle(screen, GameConfig.RED, p2, 30, 4)
    for pig in list(pigs):
        if b.body == pig.body:
            pig.life -= 20
            if pig.life <= 0:
                space.remove(pig.shape, pig.shape.body); pigs.remove(pig)
                global score; score += 10000

def post_solve_bird_wood(arbiter, space, _):
    if arbiter.total_impulse.length > 1100:
        a, b = arbiter.shapes
        for obj_list in [columns, beams]:
            for obj in list(obj_list):
                if b == obj.shape:
                    space.remove(b, b.body); obj_list.remove(obj)
                    global score; score += 5000

def post_solve_pig_wood(arbiter, space, _):
    if arbiter.total_impulse.length > 700:
        pig_shape, _ = arbiter.shapes
        for pig in list(pigs):
            if pig_shape == pig.shape:
                pig.life -= 20
                if pig.life <= 0:
                    space.remove(pig.shape, pig.shape.body); pigs.remove(pig)
                    global score; score += 10000

space.on_collision(collision_type_a=0, collision_type_b=1, post_solve=post_solve_bird_pig)
space.on_collision(collision_type_a=0, collision_type_b=2, post_solve=post_solve_bird_wood)
space.on_collision(collision_type_a=1, collision_type_b=2, post_solve=post_solve_pig_wood)

load_music()
level = Level(pigs, columns, beams, space)
level.load_level()

while running:
    x_mouse, y_mouse = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if pygame.mouse.get_pressed()[0] and is_mouse_on_slingshot(*pygame.mouse.get_pos()):
            mouse_pressed = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_pressed:
            mouse_pressed = False
            if level.number_of_birds > 0:
                level.number_of_birds -= 1; t1 = time.time()*1000
                dist = min(distance(GameConfig.SLING_X, GameConfig.SLING_Y, *pygame.mouse.get_pos()), GameConfig.ROPE_LENGTH)
                birds.append(Bird(dist if x_mouse < GameConfig.SLING_X+5 else -dist, angle, 154, 156, space))

                if level.number_of_birds == 0: t2 = time.time()
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if screen_manager.state == 1: # Pausado
                if 500 < x_mouse < 600 and 200 < y_mouse < 300: game_state = 0
                if 500 < x_mouse < 600 and 300 < y_mouse < 400: restart(); level.load_level(); game_state = 0; bird_path = []
            
            if screen_manager.state == 3: # Falha (Retry)
                if 550 < x_mouse < 670 and 455 < y_mouse < 575:
                    restart(); level.load_level(); game_state = 0; bird_path = []; score = 0; screen_manager.change(0)
            
            if screen_manager.state == 4: # Sucesso (Next/Replay)
                if 625 < x_mouse < 755 and 475 < y_mouse < 575: # Next
                    restart(); level.number += 1; game_state = 0; level.load_level(); score = 0; bird_path = []; bonus_score_once = True; screen_manager.change(0)
                elif 510 < x_mouse < 610 and 475 < y_mouse < 575: # Replay
                    restart(); level.load_level(); game_state = 0; bird_path = []; score = 0; screen_manager.change(0)

    screen.fill((130, 200, 100)); screen.blit(background2, (0, -50))
    screen.blit(sling_image, (138, 420), pygame.Rect(50, 0, 70, 220))
    for p in bird_path: pygame.draw.circle(screen, GameConfig.WHITE, p, 5, 0)
    if level.number_of_birds > 0:
        for i in range(level.number_of_birds-1): screen.blit(redbird, (100 - (i*35), 508))
    
    if mouse_pressed and level.number_of_birds > 0: sling_action()
    else:
        if time.time()*1000 - t1 > 300 and level.number_of_birds > 0: screen.blit(redbird, (130, 426))
        else: pygame.draw.line(screen, GameConfig.BLACK, (GameConfig.SLING_X, GameConfig.SLING_Y-8), (GameConfig.SLING2_X, GameConfig.SLING2_Y-7), 5)
    
    draw_level_cleared(); draw_level_failed()
    
    counter += 1
    for bird in list(birds):
        if bird.shape.body.position.y < 0: space.remove(bird.shape, bird.shape.body); birds.remove(bird); continue
        p = to_pygame(bird.shape.body.position)
        screen.blit(redbird, (p[0]-22, p[1]-20))
        if counter >= 3 and bird.shape.body.velocity.length > 20: bird_path.append(p); counter = 0
    
    for line in static_lines:
        p1, p2 = to_pygame(line.body.position + line.a), to_pygame(line.body.position + line.b)
        pygame.draw.line(screen, (150, 150, 150), p1, p2, 2)
    
    for pig in pigs:
        p = to_pygame(pig.shape.body.position)
        screen.blit(pig_image, (p[0]-22, p[1]-20))
    
    for obj in columns: obj.draw_poly('columns', screen)
    for obj in beams: obj.draw_poly('beams', screen)

    screen.blit(bold_font.render("SCORE: " + str(score), 1, GameConfig.WHITE), (1000, 90))
    screen.blit(pause_button, (10, 90))
    
    if game_state == 1:
        draw_ui_panel()
        screen.blit(bold_font3.render("PAUSED", 1, GameConfig.WHITE), (500, 90))
        screen.blit(play_button, (500, 200)); screen.blit(replay_button, (500, 300))
    
    for _ in range(2): space.step(1.0/100.0)
    pygame.display.flip(); clock.tick(50)
