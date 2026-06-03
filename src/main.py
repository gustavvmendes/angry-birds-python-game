import os
import math
import time
import pygame
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
screen_manager = ScreenManager()

# ========== GAME CONSTANTS ==========
# Window dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650

# Physics
GRAVITY = (0.0, -700.0)
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

# Collision impulse thresholds
BIRD_WOOD_IMPULSE_THRESHOLD = 1100
PIG_WOOD_IMPULSE_THRESHOLD = 700

# Image rendering offsets
BIRD_RENDER_OFFSET = 20
BIRD_SPRITE_OFFSET = 22
PIG_SPRITE_OFFSET = 15

# UI positions
LEVEL_CLEARED_RECT = (300, 0, 600, 800)
LEVEL_CLEARED_TEXT_POS = (450, 90)
SCORE_DISPLAY_POS = (550, 400)

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PANEL_BG = (35, 18, 8)
PANEL_BORDER = (210, 165, 30)
BUTTON_NORMAL = (170, 60, 20)
BUTTON_HOVER = (210, 90, 35)
BUTTON_BORDER_COLOR = (210, 165, 30)

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
redbird = pygame.image.load(
    os.path.join(IMAGES_DIR, "red-bird3.png")).convert_alpha()
background2 = pygame.image.load(
    os.path.join(IMAGES_DIR, "background3.png")).convert_alpha()
sling_image = pygame.image.load(
    os.path.join(IMAGES_DIR, "sling-3.png")).convert_alpha()
full_sprite = pygame.image.load(
    os.path.join(IMAGES_DIR, "full-sprite.png")).convert_alpha()
rect = pygame.Rect(181, 1050, 50, 50)
cropped = full_sprite.subsurface(rect).copy()
pig_image = pygame.transform.scale(cropped, (30, 30))
buttons = pygame.image.load(
    os.path.join(IMAGES_DIR, "selected-buttons.png")).convert_alpha()
pig_happy = pygame.image.load(
    os.path.join(IMAGES_DIR, "pig_failed.png")).convert_alpha()
stars = pygame.image.load(
    os.path.join(IMAGES_DIR, "stars-edited.png")).convert_alpha()
rect = pygame.Rect(0, 0, 200, 200)
star1 = stars.subsurface(rect).copy()
rect = pygame.Rect(204, 0, 200, 200)
star2 = stars.subsurface(rect).copy()
rect = pygame.Rect(426, 0, 200, 200)
star3 = stars.subsurface(rect).copy()
rect = pygame.Rect(164, 10, 60, 60)
pause_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(24, 4, 100, 100)
replay_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(142, 365, 130, 100)
next_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(18, 212, 100, 100)
play_button = buttons.subsurface(rect).copy()
clock = pygame.time.Clock()
running = True
# the base of the physics
space = pm.Space()
space.gravity = GRAVITY
pigs = []
birds = []
balls = []
polys = []
beams = []
columns = []
poly_points = []
ball_number = 0
polys_dict = {}
mouse_distance = 0
rope_lenght = ROPE_LENGTH
angle = 0
x_mouse = 0
y_mouse = 0
count = 0
mouse_pressed = False
t1 = 0
tick_to_next_circle = 10
sling_x, sling_y = SLING_X, SLING_Y
sling2_x, sling2_y = SLING2_X, SLING2_Y
score = 0
game_state = 0
screen_manager = ScreenManager()
bird_path = []
counter = 0
restart_counter = False
bonus_score_once = True
bold_font = pygame.font.SysFont("arial", 30, bold=True)
bold_font2 = pygame.font.SysFont("arial", 40, bold=True)
bold_font3 = pygame.font.SysFont("arial", 50, bold=True)
label_font = pygame.font.SysFont("arial", 22, bold=True)
wall = False
music_muted = False  # New variable to control audio state
# Custom scale matching your request (values from 0.0 to 1.0)
volume_steps = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.0]
current_volume_index = 7  # Starts at index 7, which corresponds to 0.50 (50%)
current_volume = volume_steps[current_volume_index]
volume_display_timer = 0  # Timer to control how long the volume text stays visible
small_font = pygame.font.SysFont("arial", 20, bold=True)  # Smaller font for volume

# Static floor
static_body = pm.Body(body_type=pm.Body.STATIC)
static_lines = [pm.Segment(static_body, (0.0, 060.0), (1200.0, 060.0), 0.0)]
static_lines1 = [pm.Segment(static_body, (1200.0, 060.0), (1200.0, 800.0), 0.0)]
for line in static_lines:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
for line in static_lines1:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
space.add(static_body)
for line in static_lines:
    space.add(line)


def to_pygame(p):
    """Convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+600)


def vector(p0, p1):
    """Return the vector of the points
    p0 = (xo,yo), p1 = (x1,y1)"""
    a = p1[0] - p0[0]
    b = p1[1] - p0[1]
    return (a, b)


def unit_vector(v):
    """Return the unit vector of the points
    v = (a,b)"""
    h = ((v[0]**2)+(v[1]**2))**0.5
    if h == 0:
        h = 0.000000000000001
    ua = v[0] / h
    ub = v[1] / h
    return (ua, ub)


def distance(xo, yo, x, y):
    """Calculates distance between two points."""
    origin_point = (xo, yo)
    destination_point = (x, y)
    return math.dist(origin_point, destination_point)


collision_sound = None
_last_collision_time = 0.0


def _generate_collision_sound():
    """Generate a funny descending pig squeal for bird-pig collision."""
    import array as _arr
    sample_rate, _, channels = pygame.mixer.get_init()
    sample_rate = abs(sample_rate) or 44100
    channels = channels or 2
    duration = 0.45
    n = int(sample_rate * duration)

    if _HAS_NUMPY:
        t = np.linspace(0, duration, n, dtype=np.float64)
        freq = 850.0 * np.exp(-7.0 * t) + 160.0
        freq += np.sin(2 * np.pi * 22 * t) * 55.0
        dt = duration / n
        phase = 2 * np.pi * np.cumsum(freq) * dt
        wave = np.sin(phase) + 0.45 * np.sin(2 * phase + 0.4)
        env = np.exp(-6.0 * t)
        wave *= env
        peak = np.max(np.abs(wave)) or 1.0
        wave = (wave / peak * 29000).astype(np.int16)
        if channels == 2:
            wave = np.ascontiguousarray(np.column_stack([wave, wave]))
        return pygame.sndarray.make_sound(wave)
    else:
        buf = _arr.array('h')
        phase = 0.0
        for i in range(n):
            t_i = i / sample_rate
            f = 850 * math.exp(-7 * t_i) + 160 + math.sin(2 * math.pi * 22 * t_i) * 55
            phase += 2 * math.pi * f / sample_rate
            v = math.sin(phase) + 0.45 * math.sin(2 * phase + 0.4)
            env = math.exp(-6 * t_i)
            sample = max(-32767, min(32767, int(v * env * 20000)))
            buf.append(sample)
            if channels == 2:
                buf.append(sample)
        return pygame.mixer.Sound(buffer=buf)


def load_music():
    """Load the music"""
    song1 = os.path.join(SOUNDS_DIR, 'angry-birds.ogg')
    pygame.mixer.music.load(song1)
    pygame.mixer.music.set_volume(volume_steps[current_volume_index])  # Set initial volume from scale
    pygame.mixer.music.play(-1)


def sling_action():
    """Set up sling behavior and apply maximum force limit"""
    global mouse_distance
    global rope_lenght
    global angle
    global x_mouse
    global y_mouse
    
    # Calculate current distance from sling center
    mouse_distance = distance(sling_x, sling_y, x_mouse, y_mouse)
    
    # Technical Requirement (SM 04): Implement maximum force limit constraint
    if mouse_distance > ROPE_LENGTH:
        mouse_distance = ROPE_LENGTH

    v = vector((sling_x, sling_y), (x_mouse, y_mouse))
    uv = unit_vector(v)
    uv1 = uv[0]
    uv2 = uv[1]
    
    pu = (uv1 * mouse_distance + sling_x, uv2 * mouse_distance + sling_y)
    bigger_rope = mouse_distance + 12
    x_redbird = pu[0] - BIRD_RENDER_OFFSET
    y_redbird = pu[1] - BIRD_RENDER_OFFSET
    
    # Draw the sling ropes and bird based on the constrained distance
    pygame.draw.line(screen, (0, 0, 0), (sling2_x, sling2_y), pu, 5)
    screen.blit(redbird, (x_redbird, y_redbird))
    pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y), pu, 5)
    
    # Angle of impulse
    dy = y_mouse - sling_y
    dx = x_mouse - sling_x
    if dx == 0:
        dx = 0.00000000000001
    angle = math.atan((float(dy)) / dx)


def calculate_level_bonus():
    """Calculates and updates the bonus score once."""
    global bonus_score_once, score
    if bonus_score_once:
        score += (level.number_of_birds - 1) * 10000
        bonus_score_once = False

def draw_ui_panel():
    """Draws the semi-transparent overlay and the central panel container."""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(165)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Styled panel
    panel = pygame.Rect(300, 55, 600, 560)
    pygame.draw.rect(screen, PANEL_BG, panel, border_radius=20)
    pygame.draw.rect(screen, PANEL_BORDER, panel, 5, border_radius=20)

def draw_stars():
    """Renders stars based on the achieved score."""
    if score >= level.one_star:
        screen.blit(star1, (310, 190))
    if score >= level.two_star:
        screen.blit(star2, (500, 170))
    if score >= level.three_star:
        screen.blit(star3, (700, 200))

def draw_score_text():
    """Renders the text elements for titles and scores with shadows."""
    # Title with drop shadow
    shadow = bold_font3.render("Level Cleared!", 1, (20, 10, 5))
    title = bold_font3.render("Level Cleared!", 1, WHITE)
    screen.blit(shadow, (432, 82))
    screen.blit(title, (430, 80))
    
    # Score display
    score_shadow = bold_font2.render(str(score), 1, (20, 10, 5))
    score_text = bold_font2.render(str(score), 1, WHITE)
    screen.blit(score_shadow, (552, 402))
    screen.blit(score_text, (550, 400))

def draw_interactive_button(bx, by, b_width, b_height, hover_condition, button_img, label_str, text_offset_x):
    """Generic helper to draw styled interactive menu buttons with hover effects."""
    bc = BUTTON_HOVER if hover_condition else BUTTON_NORMAL
    rr = pygame.Rect(bx - 10, by - 10, b_width, b_height)
    pygame.draw.rect(screen, bc, rr, border_radius=18)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, rr, 3, border_radius=18)
    screen.blit(button_img, (bx, by))
    lbl = label_font.render(label_str, 1, WHITE)
    screen.blit(lbl, (bx + text_offset_x, by + 103))

def draw_level_cleared():
    """Draw level cleared (Refactored to reduce cyclomatic complexity)"""
    global game_state

    # Guard clause to check if the level is actually cleared
    if level.number_of_birds < 0 or len(pigs) != 0:
        return

    calculate_level_bonus()
    screen_manager.change(4)
    
    # Render interface components
    draw_ui_panel()
    draw_stars()
    draw_score_text()
    
    # Draw interactive buttons
    hover_r = (510 <= x_mouse <= 610 and 475 <= y_mouse <= 575)
    draw_interactive_button(510, 475, 120, 120, hover_r, replay_button, "REPLAY", 10)
    
    hover_n = (625 <= x_mouse <= 755 and 475 <= y_mouse <= 575)
    draw_interactive_button(625, 475, 150, 120, hover_n, next_button, "NEXT", 40)


def draw_level_failed():
    """Draw level failed"""
    global game_state
    if level.number_of_birds <= 0 and time.time() - t2 > 5 and len(pigs) > 0:
        screen_manager.change(3)
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(165)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        # Styled panel
        panel = pygame.Rect(310, 65, 580, 525)
        pygame.draw.rect(screen, PANEL_BG, panel, border_radius=20)
        pygame.draw.rect(screen, PANEL_BORDER, panel, 5, border_radius=20)
        # Title with drop shadow
        shadow = bold_font3.render("Level Failed", 1, (20, 10, 5))
        title = bold_font3.render("Level Failed", 1, WHITE)
        screen.blit(shadow, (452, 92))
        screen.blit(title, (450, 90))
        # Pig image
        screen.blit(pig_happy, (380, 145))
        # Styled replay button
        rx, ry = 550, 455
        hover_r = (rx <= x_mouse <= rx + 100 and ry <= y_mouse <= ry + 100)
        bc = BUTTON_HOVER if hover_r else BUTTON_NORMAL
        br = pygame.Rect(rx - 10, ry - 10, 120, 120)
        pygame.draw.rect(screen, bc, br, border_radius=18)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, br, 3, border_radius=18)
        screen.blit(replay_button, (rx, ry))
        lbl = label_font.render("REPLAY", 1, WHITE)
        screen.blit(lbl, (rx + 10, ry + 103))


def _remove_objects(objects_list, space):
    """Remove objects from physics space and from the list
    
    Extracted method to eliminate code duplication.
    Used by restart() to remove pigs, birds, columns and beams.
    
    Args:
        objects_list: The list of objects to remove
        space: The pymunk physics space
    """
    objects_to_remove = []
    
    # Identify objects to remove
    for obj in objects_list:
        objects_to_remove.append(obj)
    
    # Remove from physics space and from the list
    for obj in objects_to_remove:
        space.remove(obj.shape, obj.shape.body)
        objects_list.remove(obj)


def restart():
    """Delete all objects of the level"""
    _remove_objects(pigs, space)
    _remove_objects(birds, space)
    _remove_objects(columns, space)
    _remove_objects(beams, space)


def post_solve_bird_pig(arbiter, space, _):
    """Collision between bird and pig"""
    global _last_collision_time
    surface=screen
    a, b = arbiter.shapes
    bird_body = a.body
    pig_body = b.body
    p = to_pygame(bird_body.position)
    p2 = to_pygame(pig_body.position)
    r = 30
    pygame.draw.circle(surface, BLACK, p, r, 4)
    pygame.draw.circle(surface, RED, p2, r, 4)
    pigs_to_remove = []
    for pig in pigs:
        if pig_body == pig.body:
            pig.life -= 20
            pigs_to_remove.append(pig)
            global score
            score += 10000
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    now = time.time()
    if collision_sound and now - _last_collision_time > 0.15:
        collision_sound.play()
        _last_collision_time = now


def post_solve_bird_wood(arbiter, space, _):
    """Collision between bird and wood"""
    poly_to_remove = []
    if arbiter.total_impulse.length > BIRD_WOOD_IMPULSE_THRESHOLD:
        a, b = arbiter.shapes
        for column in columns:
            if b == column.shape:
                poly_to_remove.append(column)
        for beam in beams:
            if b == beam.shape:
                poly_to_remove.append(beam)
        for poly in poly_to_remove:
            if poly in columns:
                columns.remove(poly)
            if poly in beams:
                beams.remove(poly)
        space.remove(b, b.body)
        global score
        score += 5000


def post_solve_pig_wood(arbiter, space, _):
    """Collision between pig and wood"""
    pigs_to_remove = []
    if arbiter.total_impulse.length > PIG_WOOD_IMPULSE_THRESHOLD:
        pig_shape, wood_shape = arbiter.shapes
        for pig in pigs:
            if pig_shape == pig.shape:
                pig.life -= 20
                global score
                score += 10000
                if pig.life <= 0:
                    pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


# bird and pigs
space.add_collision_handler(BIRD_COLLISION_TYPE, PIG_COLLISION_TYPE).post_solve = post_solve_bird_pig
# bird and wood
space.add_collision_handler(BIRD_COLLISION_TYPE, WOOD_COLLISION_TYPE).post_solve = post_solve_bird_wood
# pig and wood
space.add_collision_handler(PIG_COLLISION_TYPE, WOOD_COLLISION_TYPE).post_solve = post_solve_pig_wood
load_music()
try:
    collision_sound = _generate_collision_sound()
except Exception:
    collision_sound = None
level = Level(pigs, columns, beams, space)
level.number = 0
level.load_level()

while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # Toggle wall
            if wall:
                for line in static_lines1:
                    space.remove(line)
                wall = False
            else:
                for line in static_lines1:
                    space.add(line)
                wall = True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            space.gravity = (0.0, -10.0)
            level.bool_space = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            space.gravity = (0.0, -700.0)
            level.bool_space = False
            
        # Technical Requirement (SM 14): Implement Mute functionality (Key 'M')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            music_muted = not music_muted
            volume_display_timer = pygame.time.get_ticks()  # Start/Reset timer
            if music_muted:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()

        # Volume Up control (Advances to the next step in the custom volume list)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            volume_display_timer = pygame.time.get_ticks()  # Start/Reset timer
            if current_volume_index < len(volume_steps) - 1:
                current_volume_index += 1
                current_volume = volume_steps[current_volume_index]
                pygame.mixer.music.set_volume(current_volume)

        # Volume Down control (Goes back to the previous step in the custom volume list)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            volume_display_timer = pygame.time.get_ticks()  # Start/Reset timer
            if current_volume_index > 0:
                current_volume_index -= 1
                current_volume = volume_steps[current_volume_index]
                pygame.mixer.music.set_volume(current_volume)

       # Handle mouse release for the slingshot
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_pressed:
            # Release new bird
            mouse_pressed = False
            if level.number_of_birds > 0:
                level.number_of_birds -= 1
                t1 = time.time()*1000
                xo = 154
                yo = 156
                
                # Trava de Segurança (SM 04): Garante o limite máximo de força no instante do disparo
                current_dist = distance(sling_x, sling_y, x_mouse, y_mouse)
                if current_dist > ROPE_LENGTH:
                    mouse_distance = ROPE_LENGTH
                else:
                    mouse_distance = current_dist

                if x_mouse < sling_x+5:
                    bird = Bird(mouse_distance, angle, xo, yo, space)
                    birds.append(bird)
                else:
                    bird = Bird(-mouse_distance, angle, xo, yo, space)
                    birds.append(bird)
                if level.number_of_birds == 0:
                    t2 = time.time()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if (x_mouse < 60 and y_mouse < 155 and y_mouse > 90):
                screen_manager.change(1)
            if screen_manager.current() == 1:
                if x_mouse > 500 and y_mouse > 200 and y_mouse < 300:
                    # Resume in the paused screen
                    game_state = 0
                if x_mouse > 500 and y_mouse > 300:
                    # Restart in the paused screen
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
            if screen_manager.current() == 3:
                # Restart in the failed level screen
                if x_mouse > 540 and x_mouse < 660 and y_mouse > 445:
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
                    score = 0
            if screen_manager.current() == 4:
                # Build next level
                if x_mouse > 615 and y_mouse > 465:
                    restart()
                    level.number += 1
                    game_state = 0
                    level.load_level()
                    score = 0
                    bird_path = []
                    bonus_score_once = True
                if x_mouse < 615 and x_mouse > 500 and y_mouse > 465:
                    # Restart in the level cleared screen
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
                    score = 0

    # Continuous input tracking (Runs every frame, outside the event loop)
    x_mouse, y_mouse = pygame.mouse.get_pos()
    
    clicked_on_slingshot = (
        pygame.mouse.get_pressed()[0] and 
        (100 < x_mouse < 250) and 
        (370 < y_mouse < 550)
    )
    if clicked_on_slingshot:
        mouse_pressed = True

    # Draw background
    screen.fill((130, 200, 100))
    screen.blit(background2, (0, -50))
    # Draw first part of the sling
    rect = pygame.Rect(50, 0, 70, 220)
    screen.blit(sling_image, (138, 420), rect)
    # Draw the trail left behind
    for point in bird_path:
        pygame.draw.circle(screen, WHITE, point, 5, 0)
    # Draw the birds in the wait line
    if level.number_of_birds > 0:
        for i in range(level.number_of_birds-1):
            x = 100 - (i*35)
            screen.blit(redbird, (x, 508))
    # Draw sling behavior
    if mouse_pressed and level.number_of_birds > 0:
        sling_action()
    else:
        if time.time()*1000 - t1 > 300 and level.number_of_birds > 0:
            screen.blit(redbird, (130, 426))
        else:
            pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y-8),
                             (sling2_x, sling2_y-7), 5)
    birds_to_remove = []
    pigs_to_remove = []
    counter += 1
    # Draw birds
    for bird in birds:
        if bird.shape.body.position.y < 0:
            birds_to_remove.append(bird)
        p = to_pygame(bird.shape.body.position)
        x, y = p
        x -= BIRD_SPRITE_OFFSET
        y -= BIRD_RENDER_OFFSET
        screen.blit(redbird, (x, y))
        pygame.draw.circle(screen, BLUE,
                           p, int(bird.shape.radius), 2)
        if counter >= 3 and time.time() - t1 < 5:
            bird_path.append(p)
            restart_counter = True
    if restart_counter:
        counter = 0
        restart_counter = False
    # Remove birds and pigs
    for bird in birds_to_remove:
        space.remove(bird.shape, bird.shape.body)
        birds.remove(bird)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    # Draw static lines
    for line in static_lines:
        body = line.body
        pv1 = body.position + line.a.rotated(body.angle)
        pv2 = body.position + line.b.rotated(body.angle)
        p1 = to_pygame(pv1)
        p2 = to_pygame(pv2)
        pygame.draw.lines(screen, (150, 150, 150), False, [p1, p2])
    i = 0
    # Draw pigs
    for pig in pigs:
        i += 1
        pig = pig.shape
        if pig.body.position.y < 0:
            pigs_to_remove.append(pig)

        p = to_pygame(pig.body.position)
        x, y = p

        angle_degrees = math.degrees(pig.body.angle)
        img = pygame.transform.rotate(pig_image, angle_degrees)
        w,h = img.get_size()
        x -= w*0.5
        y -= h*0.5
        screen.blit(img, (x, y))
        pygame.draw.circle(screen, BLUE, p, int(pig.radius), 2)
    # Draw columns and Beams
    for column in columns:
        column.draw_poly('columns', screen)
    for beam in beams:
        beam.draw_poly('beams', screen)
    # Update physics
    dt = 1.0/50.0/2.
    for x in range(2):
        space.step(dt) # make two updates per frame for better stability
    # Drawing second part of the sling
    rect = pygame.Rect(0, 0, 60, 200)
    screen.blit(sling_image, (120, 420), rect)
    # Draw score
    score_font = bold_font.render("SCORE", 1, WHITE)
    number_font = bold_font.render(str(score), 1, WHITE)
    screen.blit(score_font, (1060, 90))
    if score == 0:
        screen.blit(number_font, (1100, 130))
    else:
        screen.blit(number_font, (1060, 130))
    screen.blit(pause_button, (10, 90))
    
    # Render and display the current volume level only when altered (lasts 2 seconds)
    current_time = pygame.time.get_ticks()
    if current_time - volume_display_timer < 2000:  # 2000ms = 2 seconds
        volume_percentage = 0 if music_muted else int(current_volume * 100)
        volume_text = f"Volume: {volume_percentage}%"
        volume_font = small_font.render(volume_text, 1, WHITE)
        screen.blit(volume_font, (1070, 610))  # Displaced slightly for better fit

    # Pause option
    if game_state == 1:
        screen.blit(play_button, (500, 200))
        screen.blit(replay_button, (500, 300))
    draw_level_cleared()
    draw_level_failed()
    pygame.display.flip()
    clock.tick(50)
    pygame.display.set_caption("fps: " + str(clock.get_fps()))
    pygame.display.set_caption("Angry Birds Python Edition")