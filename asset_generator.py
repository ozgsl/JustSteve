import pygame
import os
import math
import random

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Klasörleri oluştur
ensure_dir('assets/textures')
ensure_dir('assets/ui')
ensure_dir('assets/sounds')

pygame.init()
screen = pygame.display.set_mode((100, 100)) # Dummy ekran

def px(surface, x, y, color):
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)

def draw_from_map(surface, color_map, pixels, ox=0, oy=0):
    lines = pixels.strip().split('\n')
    for y, line in enumerate(lines):
        line = line.strip()
        for x, c in enumerate(line):
            if c in color_map:
                px(surface, ox + x, oy + y, color_map[c])

def save(surface, path, scale=None):
    if scale:
        surface = pygame.transform.scale(surface, scale)
    pygame.image.save(surface, path)

# ----------------- BLOCKS (16x16 -> 32x32) -----------------
def generate_block(name, top_color, bottom_color, spots=True):
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    s.fill(bottom_color)
    if spots:
        # Daha detayli rastgele noktalar
        random.seed(hash(name))
        for _ in range(80):
            rx, ry = random.randint(0, 15), random.randint(0, 15)
            shade = random.randint(-25, 25)
            c = (
                max(0, min(255, bottom_color[0] + shade)),
                max(0, min(255, bottom_color[1] + shade)),
                max(0, min(255, bottom_color[2] + shade))
            )
            px(s, rx, ry, c)
    # Üst kısım
    if top_color != bottom_color:
        for y in range(4):
            for x in range(16):
                shade = random.randint(-15, 15)
                c = (
                    max(0, min(255, top_color[0] + shade)),
                    max(0, min(255, top_color[1] + shade)),
                    max(0, min(255, top_color[2] + shade))
                )
                px(s, x, y, c)
                # Rastgele sarkıt (daha belirgin)
                if y == 3 and random.random() < 0.4:
                    px(s, x, y+1, c)
                    if random.random() < 0.3:
                        px(s, x, y+2, c)
                        
    # Kenar gölgelendirmesi (3D Minecraft etkisi)
    edge_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.line(edge_surf, (255, 255, 255, 60), (0, 0), (15, 0))
    pygame.draw.line(edge_surf, (255, 255, 255, 60), (0, 0), (0, 15))
    pygame.draw.line(edge_surf, (0, 0, 0, 80), (0, 15), (15, 15))
    pygame.draw.line(edge_surf, (0, 0, 0, 80), (15, 0), (15, 15))
    s.blit(edge_surf, (0, 0))
    
    save(s, f'assets/textures/{name}.png', (32, 32))

generate_block('grass', (80, 180, 60), (120, 80, 40))
generate_block('dirt', (120, 80, 40), (120, 80, 40))
generate_block('snow_grass', (240, 240, 255), (140, 160, 180))
generate_block('snow_dirt', (140, 160, 180), (140, 160, 180))
generate_block('dark_grass', (30, 80, 30), (70, 50, 30))
generate_block('dark_dirt', (70, 50, 30), (70, 50, 30))
generate_block('sand', (230, 210, 150), (230, 210, 150))
generate_block('sandstone', (230, 210, 150), (200, 180, 120), spots=False) # Çizgili yap
s = pygame.Surface((16, 16), pygame.SRCALPHA)
s.fill((230, 210, 150))
for y in [4, 8, 12]:
    for x in range(16):
        px(s, x, y, (200, 180, 120))
save(s, 'assets/textures/sandstone.png', (32, 32))

generate_block('end_stone', (220, 230, 160), (220, 230, 160))
generate_block('purpur', (160, 120, 180), (160, 120, 180))
generate_block('stone', (140, 140, 140), (140, 140, 140))
s_ice = pygame.Surface((16, 16), pygame.SRCALPHA)
s_ice.fill((160, 200, 255, 200))
for x in range(16):
    px(s_ice, x, 0, (200, 230, 255, 220))
    px(s_ice, 0, x, (200, 230, 255, 220))
save(s_ice, 'assets/textures/ice.png', (32, 32))
generate_block('dark_wood', (60, 40, 20), (60, 40, 20))

# Soru bloğu
def gen_qb(hit=False):
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    s.fill((120, 80, 40) if hit else (220, 170, 40))
    pygame.draw.rect(s, (0,0,0), (0,0,16,16), 1)
    if not hit:
        qb_map = { 'Y': (255, 255, 100), 'O': (200, 120, 20) }
        qb_pix = """
        ..YYYY..
        .YY..YY.
        .YY..YY.
        ....YY..
        ...YY...
        ...YY...
        ........
        ...YY...
        """
        draw_from_map(s, qb_map, qb_pix, 4, 4)
    save(s, 'assets/textures/question_block_hit.png' if hit else 'assets/textures/question_block.png', (32, 32))
gen_qb(False)
gen_qb(True)

# ----------------- CHARACTERS (14x19 -> 28x38) -----------------
char_map_base = {
    'S': (234, 192, 134), # Skin
    'H': (88, 56, 34),    # Hair
    'C': (0, 170, 170),   # Cyan shirt
    'B': (61, 61, 142),   # Blue pants
    'G': (80, 80, 80),    # Shoes
    'E': (255, 255, 255), # Eye white
    'P': (0, 0, 0),       # Pupil
}

def draw_char(s, cmap, frame):
    head = """
    .HHHHHH.
    .HSSSSH.
    HSSSSSSH
    HSESESH.
    HSPSPSH.
    HSSSSSSH
    .HSSSSH.
    """
    body = """
    ..CCCC..
    .CCCCCC.
    .SCCCCS.
    .SCCCCS.
    ..CCCC..
    ..CCCC..
    """
    legs = {
        'idle_0': """
        ..BBBB..
        ..BBBB..
        ..BBBB..
        ..BBBB..
        ..GGGG..
        """,
        'idle_1': """
        ..BBBB..
        ..BBBB..
        ..BBBB..
        ..BBBB..
        ..GGGG..
        """, # Vücut biraz aşağı kayacak
        'run_0': """
        ..B..B..
        ..B..B..
        ..B..B..
        ..B..B..
        ..G..G..
        """,
        'run_1': """
        ...BB...
        ...BB...
        ...BB...
        ...BB...
        ...GG...
        """,
        'jump': """
        ..B..B..
        ..B..B..
        ..B..B..
        .B....B.
        .G....G.
        """
    }
    
    draw_from_map(s, cmap, head, 3, 0)
    dy = 1 if frame == 'idle_1' else 0
    draw_from_map(s, cmap, body, 3, 7 + dy)
    
    if frame == 'jump':
        # Kollar yukarıda
        for y in range(4):
            px(s, 2, 7+y, cmap['S'])
            px(s, 11, 7+y, cmap['S'])
            
    draw_from_map(s, cmap, legs[frame], 3, 13 + dy)

for frame in ['idle_0', 'idle_1', 'run_0', 'run_1', 'jump']:
    s = pygame.Surface((14, 19), pygame.SRCALPHA)
    draw_char(s, char_map_base, frame)
    save(s, f'assets/textures/steve_{frame}.png', (28, 38))

# Alex
alex_map = char_map_base.copy()
alex_map['H'] = (180, 100, 30) # Auburn
alex_map['C'] = (76, 153, 0) # Green shirt
alex_map['B'] = (100, 70, 40) # Brown pants
s = pygame.Surface((14, 19), pygame.SRCALPHA)
draw_char(s, alex_map, 'idle_0')
save(s, 'assets/textures/alex.png', (28, 38))

# Zombie
zom_map = char_map_base.copy()
zom_map['S'] = (69, 137, 56)
zom_map['P'] = (20, 40, 20)
for i in [0, 1]:
    s = pygame.Surface((14, 19), pygame.SRCALPHA)
    draw_char(s, zom_map, f'run_{i}')
    # Kollari ileri uzat
    pygame.draw.rect(s, (0,0,0,0), (0, 7, 14, 6)) # Koları temizle
    body_pix = """
    ..CCCC..
    .CCCCCC.
    .SCCCCS.
    .SCCCCS.
    ..CCCC..
    ..CCCC..
    """
    draw_from_map(s, zom_map, body_pix, 3, 7) # Sadece gövde
    # İleri kol
    for x in range(3, 9):
        px(s, x, 8, zom_map['C'])
        px(s, x, 9, zom_map['S'])
    save(s, f'assets/textures/zombie_{i}.png', (28, 38))

# Skeleton
skel_map = char_map_base.copy()
skel_map['S'] = (220, 220, 220)
skel_map['H'] = (220, 220, 220)
skel_map['C'] = (200, 200, 200) # Kaburga
skel_map['B'] = (220, 220, 220)
for i in [0, 1]:
    s = pygame.Surface((14, 19), pygame.SRCALPHA)
    draw_char(s, skel_map, f'run_{i}')
    save(s, f'assets/textures/skeleton_{i}.png', (28, 38))

# Enderman (uzun)
for i in [0, 1]:
    s = pygame.Surface((14, 19), pygame.SRCALPHA)
    s.fill((0,0,0,0))
    b = (20, 20, 20)
    p = (180, 60, 220)
    pygame.draw.rect(s, b, (5, 0, 4, 4))
    pygame.draw.rect(s, p, (5, 1, 2, 1))
    pygame.draw.rect(s, b, (6, 4, 2, 8))
    # Bacaklar
    if i == 0:
        pygame.draw.rect(s, b, (5, 12, 1, 7))
        pygame.draw.rect(s, b, (8, 12, 1, 7))
    else:
        pygame.draw.rect(s, b, (6, 12, 2, 7))
    save(s, f'assets/textures/enderman_{i}.png', (28, 38))

# Creeper
for i in [0, 1]:
    s = pygame.Surface((14, 19), pygame.SRCALPHA)
    g = (80, 170, 60)
    k = (0,0,0)
    pygame.draw.rect(s, g, (4, 4, 6, 6))
    pygame.draw.rect(s, k, (5, 6, 1, 1))
    pygame.draw.rect(s, k, (8, 6, 1, 1))
    pygame.draw.rect(s, k, (6, 7, 2, 2))
    pygame.draw.rect(s, k, (5, 8, 1, 2))
    pygame.draw.rect(s, k, (8, 8, 1, 2))
    pygame.draw.rect(s, g, (5, 10, 4, 6))
    if i == 0:
        pygame.draw.rect(s, g, (4, 16, 2, 3))
        pygame.draw.rect(s, g, (8, 16, 2, 3))
    else:
        pygame.draw.rect(s, g, (5, 16, 4, 3))
    save(s, f'assets/textures/creeper_{i}.png', (28, 38))

# ----------------- OBJECTS -----------------
# Emerald
em_map = { 'D': (20, 140, 40), 'L': (60, 220, 80), 'H': (180, 255, 200) }
for i in range(4):
    s = pygame.Surface((10, 10), pygame.SRCALPHA)
    if i % 2 == 0:
        pix = """
        ...D...
        ..LHL..
        .LHHHL.
        DHHHHLD
        .LLHLL.
        ..LDL..
        ...D...
        """
        draw_from_map(s, em_map, pix, 1, 1)
    else:
        pix = """
        ...D...
        ...H...
        ..LHL..
        ..LHL..
        ..LHL..
        ...D...
        .......
        """
        draw_from_map(s, em_map, pix, 1, 1)
    save(s, f'assets/textures/emerald_{i}.png', (22, 22))

# Hearts
s = pygame.Surface((12, 12), pygame.SRCALPHA)
pygame.draw.circle(s, (220, 20, 20), (3, 3), 3)
pygame.draw.circle(s, (220, 20, 20), (8, 3), 3)
pygame.draw.polygon(s, (220, 20, 20), [(1, 5), (10, 5), (6, 10)])
save(s, 'assets/textures/heart_full.png', (24, 24))

s = pygame.Surface((12, 12), pygame.SRCALPHA)
pygame.draw.circle(s, (80, 80, 80), (3, 3), 3)
pygame.draw.circle(s, (80, 80, 80), (8, 3), 3)
pygame.draw.polygon(s, (80, 80, 80), [(1, 5), (10, 5), (6, 10)])
save(s, 'assets/textures/heart_empty.png', (24, 24))

# Mushroom
s = pygame.Surface((14, 14), pygame.SRCALPHA)
pygame.draw.circle(s, (200, 40, 40), (7, 6), 5)
pygame.draw.rect(s, (220, 200, 180), (5, 8, 4, 6))
px(s, 5, 4, (255, 255, 255))
px(s, 8, 3, (255, 255, 255))
px(s, 9, 6, (255, 255, 255))
save(s, 'assets/textures/mushroom.png', (28, 28))

# Arrow
s = pygame.Surface((12, 4), pygame.SRCALPHA)
pygame.draw.rect(s, (139, 69, 19), (2, 1, 8, 2)) # Şaft
px(s, 10, 1, (100, 100, 100))
px(s, 11, 1, (150, 150, 150))
px(s, 0, 0, (200, 200, 200)) # Tüy
px(s, 0, 2, (200, 200, 200))
save(s, 'assets/textures/arrow.png', (24, 8))

# Particle
s = pygame.Surface((4, 4), pygame.SRCALPHA)
s.fill((255, 255, 255))
save(s, 'assets/textures/particle.png', (8, 8))

# ----------------- DECORATIONS -----------------
# Sun
s = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(s, (255, 240, 50), (12, 12), 8)
pygame.draw.rect(s, (255, 240, 50), (10, 0, 4, 24))
pygame.draw.rect(s, (255, 240, 50), (0, 10, 24, 4))
save(s, 'assets/textures/sun.png', (48, 48))

# Cloud
s = pygame.Surface((32, 12), pygame.SRCALPHA)
pygame.draw.rect(s, (255, 255, 255), (4, 4, 24, 8))
pygame.draw.rect(s, (255, 255, 255), (8, 0, 16, 6))
save(s, 'assets/textures/cloud.png', (96, 36))

# Trees (40x60 -> drawn approx)
def gen_tree(name, trunk_color, leaf_color, shape='round'):
    s = pygame.Surface((20, 30), pygame.SRCALPHA)
    pygame.draw.rect(s, trunk_color, (8, 15, 4, 15))
    if shape == 'round':
        pygame.draw.circle(s, leaf_color, (10, 10), 8)
    elif shape == 'pine':
        pygame.draw.polygon(s, leaf_color, [(10, 0), (2, 18), (18, 18)])
    elif shape == 'cactus':
        pygame.draw.rect(s, leaf_color, (8, 5, 4, 25))
        pygame.draw.rect(s, leaf_color, (4, 10, 4, 4))
        pygame.draw.rect(s, leaf_color, (4, 8, 2, 4))
        pygame.draw.rect(s, leaf_color, (12, 15, 4, 4))
        pygame.draw.rect(s, leaf_color, (14, 13, 2, 4))
    elif shape == 'chorus':
        pygame.draw.rect(s, leaf_color, (8, 5, 4, 25))
        pygame.draw.rect(s, leaf_color, (4, 10, 4, 4))
        pygame.draw.rect(s, (200, 150, 220), (4, 6, 4, 4)) # cicek
        pygame.draw.rect(s, leaf_color, (12, 15, 4, 4))
        pygame.draw.rect(s, (200, 150, 220), (12, 11, 4, 4))
    save(s, f'assets/textures/tree_{name}.png', (40, 64))

gen_tree('oak', (100, 60, 30), (50, 150, 50), 'round')
gen_tree('spruce', (80, 50, 20), (30, 90, 40), 'pine')
gen_tree('dark_oak', (50, 30, 10), (20, 80, 20), 'round')
gen_tree('cactus', (0,0,0,0), (40, 160, 40), 'cactus')
gen_tree('chorus', (0,0,0,0), (120, 80, 160), 'chorus')

# Grass tuft
s = pygame.Surface((12, 8), pygame.SRCALPHA)
pygame.draw.rect(s, (60, 180, 60), (2, 4, 2, 4))
pygame.draw.rect(s, (60, 180, 60), (5, 2, 2, 6))
pygame.draw.rect(s, (60, 180, 60), (8, 5, 2, 3))
save(s, 'assets/textures/grass_tuft.png', (24, 16))

# Portal
for i in range(4):
    s = pygame.Surface((32, 48), pygame.SRCALPHA)
    pygame.draw.rect(s, (30, 10, 50), (0, 0, 32, 48))
    # Obsidian frame
    pygame.draw.rect(s, (20, 10, 30), (0, 0, 32, 48), 4)
    # Swirls
    import random
    random.seed(i)
    for _ in range(40):
        x = random.randint(4, 26)
        y = random.randint(4, 42)
        pygame.draw.rect(s, (150, 50, 220, 150), (x, y, 4, 4))
        pygame.draw.rect(s, (200, 100, 255, 180), (x+1, y+1, 2, 2))
    save(s, f'assets/textures/portal_{i}.png', (64, 96))

# Explosion
for i in range(4):
    s = pygame.Surface((30, 30), pygame.SRCALPHA)
    r = (i + 1) * 7
    pygame.draw.circle(s, (255, 200, 50), (15, 15), r)
    pygame.draw.circle(s, (255, 100, 20), (15, 15), int(r * 0.7))
    pygame.draw.circle(s, (255, 50, 0), (15, 15), int(r * 0.4))
    save(s, f'assets/textures/explosion_{i}.png', (60, 60))

# Skills
s = pygame.Surface((12, 12), pygame.SRCALPHA)
pygame.draw.arc(s, (150, 200, 255), (2, 2, 8, 8), 0, math.pi, 2)
pygame.draw.arc(s, (150, 200, 255), (4, 4, 4, 4), 0, math.pi, 2)
save(s, 'assets/textures/skill_doublejump.png', (24, 24))

s = pygame.Surface((12, 12), pygame.SRCALPHA)
pygame.draw.rect(s, (200, 100, 255), (3, 6, 6, 6))
pygame.draw.rect(s, (255, 255, 255), (4, 7, 2, 2))
pygame.draw.rect(s, (100, 50, 120), (5, 2, 2, 4))
save(s, 'assets/textures/skill_shrink.png', (24, 24))

# ----------------- UI -----------------
# Button
s = pygame.Surface((100, 20), pygame.SRCALPHA)
pygame.draw.rect(s, (120, 120, 120), (0, 0, 100, 20))
pygame.draw.rect(s, (180, 180, 180), (0, 0, 100, 20), 2)
pygame.draw.rect(s, (60, 60, 60), (0, 18, 100, 2))
pygame.draw.rect(s, (60, 60, 60), (98, 0, 2, 20))
save(s, 'assets/ui/button.png', (200, 50))

# Touch buttons
def draw_touch(name, symbol_fn):
    s = pygame.Surface((70, 70), pygame.SRCALPHA)
    pygame.draw.circle(s, (200, 200, 200, 150), (35, 35), 35)
    pygame.draw.circle(s, (255, 255, 255, 200), (35, 35), 35, 2)
    symbol_fn(s)
    save(s, f'assets/ui/btn_{name}.png')

def sym_left(s): pygame.draw.polygon(s, (255, 255, 255), [(20, 35), (45, 15), (45, 55)])
def sym_right(s): pygame.draw.polygon(s, (255, 255, 255), [(50, 35), (25, 15), (25, 55)])
def sym_jump(s): pygame.draw.circle(s, (255, 255, 255), (35, 35), 15)
def sym_dash(s):
    pygame.draw.rect(s, (255, 255, 255), (20, 30, 20, 10))
    pygame.draw.polygon(s, (255, 255, 255), [(40, 20), (60, 35), (40, 50)])

draw_touch('left', sym_left)
draw_touch('right', sym_right)
draw_touch('jump', sym_jump)
draw_touch('dash', sym_dash)

print("[OK] All assets generated successfully!")
