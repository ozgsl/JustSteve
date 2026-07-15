# settings.py - JustSteve v2 - Biyomlar, Skill Sistemi, Portal

# -- Ekran --
WIDTH = 960
HEIGHT = 540
FPS = 60
TILE_SIZE = 32

# -- Fizik --
GRAVITY = 0.55
MAX_FALL_SPEED = 14
JUMP_FORCE = -12.5
MOVE_SPEED = 4.5

# -- Hollow Knight Mekanigi --
COYOTE_TIME = 7
JUMP_BUFFER = 7
VARIABLE_JUMP_CUT = 0.4
DASH_SPEED = 14
DASH_DURATION = 8
DASH_COOLDOWN = 40

# -- Oyuncu --
PLAYER_WIDTH = 28
PLAYER_HEIGHT = 38
PLAYER_MAX_HP = 10
INVINCIBILITY_FRAMES = 90
SHRINK_SCALE = 0.55      # Kucuk boyut carpani
SHRINK_DURATION = 600     # 10 saniye

# -- Dusmanlar --
ZOMBIE_SPEED = 1.2
SKELETON_SPEED = 1.0
ENDERMAN_SPEED = 2.5
CREEPER_SPEED = 1.0
ARROW_SPEED = 5
SKELETON_SHOOT_CD = 120
CREEPER_FUSE_DIST = 80    # piksel - patlamaya basladigi mesafe
CREEPER_FUSE_TIME = 90    # frame (1.5 sn)
CREEPER_EXPLODE_RADIUS = 100
ENDERMAN_TP_CD = 150      # teleport bekleme suresi (frame)
ENDERMAN_TP_RANGE = 120   # ne kadar yakin teleport eder
MOB_CHASE_RANGE = 300     # piksel - bu mesafeden takibe baslar

# -- Prosedürel Seviye --
CHUNK_COLS = 16
CHUNK_WIDTH = CHUNK_COLS * TILE_SIZE
GROUND_ROW = 13
TOTAL_ROWS = 17
KILL_Y = TOTAL_ROWS * TILE_SIZE + 100

LEVEL_DISTANCES = [4000, 5500, 7000, 8500, 10000]
LEVEL_DIFFICULTY = [
    (0.10, 0.18, 1.0),
    (0.14, 0.24, 1.1),
    (0.18, 0.30, 1.2),
    (0.22, 0.36, 1.3),
    (0.26, 0.42, 1.4),
]

# -- Biyomlar (her seviye icin) --
BIOMES = [
    {   # Seviye 1: Ovalar (Plains)
        'name': 'Ovalar',
        'sky_top': (110, 180, 250), 'sky_bottom': (170, 215, 255),
        'ground': 'grass', 'under': 'dirt', 'platform': 'stone',
        'tree': 'oak', 'cloud_color': (255, 255, 255),
    },
    {   # Seviye 2: Kar (Snow/Taiga)
        'name': 'Kar Biyomu',
        'sky_top': (180, 200, 235), 'sky_bottom': (210, 225, 245),
        'ground': 'snow_grass', 'under': 'snow_dirt', 'platform': 'ice',
        'tree': 'spruce', 'cloud_color': (220, 230, 245),
    },
    {   # Seviye 3: Kalin Orman (Dark Forest)
        'name': 'Karanlik Orman',
        'sky_top': (40, 60, 40), 'sky_bottom': (70, 95, 60),
        'ground': 'dark_grass', 'under': 'dark_dirt', 'platform': 'dark_wood',
        'tree': 'dark_oak', 'cloud_color': (100, 110, 90),
    },
    {   # Seviye 4: Col (Desert)
        'name': 'Col',
        'sky_top': (180, 160, 110), 'sky_bottom': (230, 210, 160),
        'ground': 'sand', 'under': 'sandstone', 'platform': 'sandstone',
        'tree': 'cactus', 'cloud_color': (240, 235, 220),
    },
    {   # Seviye 5: End
        'name': 'The End',
        'sky_top': (10, 5, 35), 'sky_bottom': (25, 15, 55),
        'ground': 'end_stone', 'under': 'end_stone', 'platform': 'purpur',
        'tree': 'chorus', 'cloud_color': (60, 40, 80),
    },
]

# -- UI --
HEART_SIZE = 24
HEART_SPACING = 28
EMERALD_ICON_SIZE = 22
TOUCH_BTN_SIZE = 70
TOUCH_BTN_ALPHA = 130

# -- Portal --
PORTAL_WIDTH = 64
PORTAL_HEIGHT = 96
