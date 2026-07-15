"""
sprites.py - JustSteve v2
Mob AI (takip), Creeper patlama, Enderman teleport, skill drop,
double jump, shrink, portal, dekorasyon
"""
import pygame
import math
import random
from settings import *

def load_img(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        s = pygame.Surface(size or (32, 32), pygame.SRCALPHA)
        s.fill((255, 0, 255, 120))
        return s

# =====================================================================
# PLAYER
# =====================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._base_size = (PLAYER_WIDTH, PLAYER_HEIGHT)
        self._current_scale = 1.0
        self.load_animations(self._base_size)

        self.state = 'idle'
        self.anim_index = 0
        self.anim_timer = 0
        self.facing_right = True

        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Fizik
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = MOVE_SPEED
        self.on_ground = False

        # HK mekanikleri
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.jump_held = False

        # Dash
        self.dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.dash_dir = 1

        # Can
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.invincible = False
        self.invincible_timer = 0
        self.alive = True

        # Skill: Double Jump
        self.has_double_jump = False
        self.double_jump_used = False

        # Skill: Shrink
        self.is_shrunk = False
        self.shrink_timer = 0

        # Skor
        self.emeralds = 0
        self.world_x = 0

        # Ses
        self.jump_sound = self._snd('assets/sounds/jump.ogg')
        self.hit_sound = self._snd('assets/sounds/hit.ogg')

    def _snd(self, p):
        try: return pygame.mixer.Sound(p)
        except: return None

    def load_animations(self, sz):
        self.animations = {
            'idle': [load_img(f'assets/textures/steve_idle_{i}.png', sz) for i in range(2)],
            'run':  [load_img(f'assets/textures/steve_run_{i}.png', sz) for i in range(2)],
            'jump': [load_img('assets/textures/steve_jump.png', sz)],
            'fall': [load_img('assets/textures/steve_idle_0.png', sz)],
        }

    def take_damage(self, amount=1):
        if self.invincible or not self.alive: return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0; self.alive = False
        else:
            self.invincible = True
            self.invincible_timer = INVINCIBILITY_FRAMES
        if self.hit_sound: self.hit_sound.play()

    def heal(self, amount=1):
        self.hp = min(self.hp + amount, self.max_hp)

    def activate_shrink(self):
        if not self.is_shrunk:
            self.is_shrunk = True
            self.shrink_timer = SHRINK_DURATION
            self._current_scale = SHRINK_SCALE
            sz = (int(PLAYER_WIDTH * SHRINK_SCALE), int(PLAYER_HEIGHT * SHRINK_SCALE))
            bottom = self.rect.bottom
            cx = self.rect.centerx
            self.load_animations(sz)
            self.image = self.animations[self.state][0]
            self.rect = self.image.get_rect(midbottom=(cx, bottom))

    def deactivate_shrink(self):
        if self.is_shrunk:
            self.is_shrunk = False
            self._current_scale = 1.0
            bottom = self.rect.bottom
            cx = self.rect.centerx
            self.load_animations(self._base_size)
            self.image = self.animations[self.state][0]
            self.rect = self.image.get_rect(midbottom=(cx, bottom))

    def activate_double_jump(self):
        self.has_double_jump = True

    def request_jump(self):
        self.jump_buffer_timer = JUMP_BUFFER

    def release_jump(self):
        if self.vel.y < 0:
            self.vel.y *= VARIABLE_JUMP_CUT
        self.jump_held = False

    def start_dash(self):
        if self.dash_cooldown_timer <= 0 and not self.dashing:
            self.dashing = True
            self.dash_timer = DASH_DURATION
            self.dash_cooldown_timer = DASH_COOLDOWN
            self.dash_dir = 1 if self.facing_right else -1

    def _try_jump(self):
        if self.coyote_timer > 0:
            speed_bonus = (abs(self.vel.x) / MAX_SPEED) * 1.5
            self.vel.y = JUMP_FORCE - speed_bonus
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
            self.on_ground = False
            self.jump_held = True
            self.double_jump_used = False
            if self.jump_sound: self.jump_sound.play()
        elif self.has_double_jump and not self.double_jump_used and not self.on_ground:
            self.vel.y = JUMP_FORCE * 0.85
            self.double_jump_used = True
            self.jump_buffer_timer = 0
            if self.jump_sound: self.jump_sound.play()

    def update_timers(self):
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
            self.double_jump_used = False
        else:
            if self.coyote_timer > 0: self.coyote_timer -= 1

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            self._try_jump()

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0: self.invincible = False

        if self.dash_cooldown_timer > 0: self.dash_cooldown_timer -= 1
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.dashing = False

        if self.is_shrunk:
            self.shrink_timer -= 1
            if self.shrink_timer <= 0:
                self.deactivate_shrink()

    def apply_gravity(self):
        if not self.dashing:
            self.vel.y += GRAVITY
            if self.vel.y > MAX_FALL_SPEED: self.vel.y = MAX_FALL_SPEED

    def update_animation(self):
        self.anim_timer += 1
        if self.dashing:
            ns = 'run'
        elif not self.on_ground:
            ns = 'jump' if self.vel.y < 0 else 'fall'
        elif abs(self.vel.x) > 0.5:
            ns = 'run'
        else:
            ns = 'idle'

        if ns != self.state:
            self.state = ns; self.anim_index = 0; self.anim_timer = 0

        frames = self.animations[self.state]
        spd = 8 if self.state == 'run' else 20
        if self.anim_timer >= spd:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)

        self.image = frames[self.anim_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.invincible and self.invincible_timer % 6 < 3:
            self.image = self.image.copy()
            self.image.set_alpha(80)

    def update(self):
        if not self.alive: return
        self.update_timers()
        self.update_animation()


# =====================================================================
# ENEMY BASE
# =====================================================================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, img_prefix, speed, hp=1):
        super().__init__()
        sz = (PLAYER_WIDTH, PLAYER_HEIGHT)
        self.frames = [load_img(f'assets/textures/{img_prefix}_{i}.png', sz) for i in range(2)]
        self.anim_index = 0
        self.anim_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.direction = -1
        self.hp = hp
        self.alive = True
        self.vel_y = 0
        self.on_ground = False
        self.drops_heart = False
        self.player_ref = None   # seviye tarafindan set edilecek

    def take_hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            self.kill()
            return True
        return False

    def _chase_player(self):
        """Oyuncuyu takip et."""
        if self.player_ref and self.player_ref.alive:
            dx = self.player_ref.rect.centerx - self.rect.centerx
            if abs(dx) < MOB_CHASE_RANGE:
                self.direction = 1 if dx > 0 else -1

    def update(self):
        if not self.alive: return
        self._chase_player()
        self.rect.x += self.speed * self.direction
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED: self.vel_y = MAX_FALL_SPEED
        self.rect.y += self.vel_y

        self.anim_timer += 1
        if self.anim_timer >= 15:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.frames)
        img = self.frames[self.anim_index]
        if self.direction > 0:
            img = pygame.transform.flip(img, True, False)
        self.image = img


class Zombie(Enemy):
    def __init__(self, x, y, sm=1.0):
        super().__init__(x, y, 'zombie', ZOMBIE_SPEED * sm)


class Skeleton(Enemy):
    def __init__(self, x, y, sm=1.0):
        super().__init__(x, y, 'skeleton', SKELETON_SPEED * sm)
        self.shoot_timer = SKELETON_SHOOT_CD
        self.arrows = pygame.sprite.Group()

    def update(self):
        super().update()
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = SKELETON_SHOOT_CD
            # Oyuncuya dogru ates
            if self.player_ref and self.player_ref.alive:
                dx = self.player_ref.rect.centerx - self.rect.centerx
                d = 1 if dx > 0 else -1
            else:
                d = self.direction
            arrow = Arrow(self.rect.centerx, self.rect.centery, d)
            self.arrows.add(arrow)


class Enderman(Enemy):
    """Isınlanıp saldıran Enderman."""
    def __init__(self, x, y, sm=1.0):
        super().__init__(x, y, 'enderman', ENDERMAN_SPEED * sm)
        self.tp_timer = ENDERMAN_TP_CD
        self.tp_particles = []

    def update(self):
        if not self.alive: return
        # Normal animasyon
        self.anim_timer += 1
        if self.anim_timer >= 15:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.frames)
        img = self.frames[self.anim_index]
        if self.direction > 0:
            img = pygame.transform.flip(img, True, False)
        self.image = img

        # Yercekimi
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED: self.vel_y = MAX_FALL_SPEED
        self.rect.y += self.vel_y

        # Teleport
        self.tp_timer -= 1
        if self.tp_timer <= 0 and self.player_ref and self.player_ref.alive:
            self.tp_timer = ENDERMAN_TP_CD
            px = self.player_ref.rect.centerx
            py = self.player_ref.rect.top
            offset = random.choice([-ENDERMAN_TP_RANGE, ENDERMAN_TP_RANGE])
            self.rect.centerx = px + offset
            self.rect.bottom = py
            self.vel_y = 0
            self.direction = 1 if offset < 0 else -1
        else:
            self._chase_player()
            self.rect.x += self.speed * self.direction


class Creeper(Enemy):
    """Yaklasininca patlayan Creeper."""
    def __init__(self, x, y, sm=1.0):
        super().__init__(x, y, 'creeper', CREEPER_SPEED * sm, hp=2)
        self.drops_heart = True
        self.fusing = False
        self.fuse_timer = 0
        self.exploded = False

    def update(self):
        if not self.alive or self.exploded: return

        # Animasyon
        self.anim_timer += 1
        if self.anim_timer >= 15:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.frames)
        img = self.frames[self.anim_index]
        if self.direction > 0:
            img = pygame.transform.flip(img, True, False)

        # Yercekimi
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED: self.vel_y = MAX_FALL_SPEED
        self.rect.y += self.vel_y

        self._chase_player()

        # Fuse kontrolu
        if self.player_ref and self.player_ref.alive:
            dist = abs(self.player_ref.rect.centerx - self.rect.centerx)
            if dist < CREEPER_FUSE_DIST:
                if not self.fusing:
                    self.fusing = True
                    self.fuse_timer = CREEPER_FUSE_TIME
                self.fuse_timer -= 1
                # Yanip sonme efekti
                if self.fuse_timer % 10 < 5:
                    flash = img.copy()
                    white = pygame.Surface(flash.get_size(), pygame.SRCALPHA)
                    white.fill((255, 255, 255, 120))
                    flash.blit(white, (0, 0))
                    img = flash
                if self.fuse_timer <= 0:
                    self.exploded = True
                    return
            else:
                self.fusing = False
                self.rect.x += self.speed * self.direction

        self.image = img


# =====================================================================
# PROJECTILES & EFFECTS
# =====================================================================
class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = load_img('assets/textures/arrow.png', (24, 8))
        if direction > 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ARROW_SPEED * direction
        self.lifetime = 180

    def update(self):
        self.rect.x += self.speed
        self.lifetime -= 1
        if self.lifetime <= 0: self.kill()


class Explosion(pygame.sprite.Sprite):
    """Creeper patlama animasyonu."""
    def __init__(self, x, y):
        super().__init__()
        self.frames = [load_img(f'assets/textures/explosion_{i}.png', (60, 60)) for i in range(4)]
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0
        self.radius = CREEPER_EXPLODE_RADIUS

    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return
            self.image = self.frames[self.frame_index]


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color=(255, 255, 255), vel=None):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 4, 4))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = vel[0] if vel else random.uniform(-3, 3)
        self.vel_y = vel[1] if vel else random.uniform(-5, -1)
        self.lifetime = 20

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 0.2
        self.lifetime -= 1
        if self.lifetime <= 0: self.kill()


# =====================================================================
# BLOCKS & ITEMS
# =====================================================================
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, img_path):
        super().__init__()
        self.image = load_img(img_path, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))


class QuestionBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_normal = load_img('assets/textures/question_block.png', (TILE_SIZE, TILE_SIZE))
        self.image_hit = load_img('assets/textures/question_block_hit.png', (TILE_SIZE, TILE_SIZE))
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        self.was_hit = False
        self.bounce_offset = 0
        self.bouncing = False

    def hit(self):
        if not self.was_hit:
            self.was_hit = True
            self.image = self.image_hit
            self.bouncing = True
            self.bounce_offset = -8
            return True
        return False

    def update(self):
        if self.bouncing:
            self.bounce_offset += 2
            if self.bounce_offset >= 0:
                self.bounce_offset = 0
                self.bouncing = False

    def draw_offset(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y + self.bounce_offset))


class Emerald(pygame.sprite.Sprite):
    def __init__(self, x, y, from_block=False):
        super().__init__()
        self.frames = [load_img(f'assets/textures/emerald_{i}.png', (EMERALD_ICON_SIZE, EMERALD_ICON_SIZE)) for i in range(4)]
        self.anim_index = 0; self.anim_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.from_block = from_block
        self.vel_y = -6 if from_block else 0

    def update(self):
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % 4
        self.image = self.frames[self.anim_index]
        if self.from_block:
            self.vel_y += 0.3
            self.rect.y += self.vel_y
            if self.vel_y > 5: self.from_block = False


class HeartPickup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_img('assets/textures/heart_full.png', (HEART_SIZE, HEART_SIZE))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -5
        self.lifetime = 300

    def update(self):
        self.vel_y += 0.3
        self.rect.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime <= 0: self.kill()


class SkillDrop(pygame.sprite.Sprite):
    """Mob oldugunce dusen skill: 'double_jump' veya 'shrink'."""
    def __init__(self, x, y, skill_type):
        super().__init__()
        self.skill_type = skill_type
        img_name = f'skill_{skill_type}.png'
        self.image = load_img(f'assets/textures/{img_name}', (24, 24))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -4
        self.lifetime = 360
        self.bob_timer = 0

    def update(self):
        self.vel_y += 0.25
        self.rect.y += self.vel_y
        self.lifetime -= 1
        # Hafif sallanma
        self.bob_timer += 1
        if self.vel_y <= 0:
            pass
        if self.lifetime <= 0: self.kill()


# =====================================================================
# PORTAL
# =====================================================================
class Portal(pygame.sprite.Sprite):
    """Seviye sonu portali."""
    def __init__(self, x, y):
        super().__init__()
        self.frames = [load_img(f'assets/textures/portal_{i}.png', (PORTAL_WIDTH, PORTAL_HEIGHT)) for i in range(4)]
        self.anim_index = 0; self.anim_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(x, y))

    def update(self):
        self.anim_timer += 1
        if self.anim_timer >= 6:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % 4
        self.image = self.frames[self.anim_index]


# =====================================================================
# DECORATIONS
# =====================================================================
class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, color=(255, 255, 255)):
        super().__init__()
        self.image = load_img('assets/textures/cloud.png', (96, 36))
        # Renk tonu uygula
        tinted = self.image.copy()
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill((*color, 60))
        tinted.blit(overlay, (0, 0))
        self.image = tinted
        self.rect = self.image.get_rect(topleft=(x, y))
        self.parallax = 0.3  # kameradan yavas kayar

    def draw(self, surface, camera_x):
        sx = self.rect.x - camera_x * self.parallax
        surface.blit(self.image, (sx, self.rect.y))


class TreeDecor(pygame.sprite.Sprite):
    def __init__(self, x, y, tree_type='oak'):
        super().__init__()
        self.image = load_img(f'assets/textures/tree_{tree_type}.png', (40, 64))
        self.rect = self.image.get_rect(midbottom=(x, y))

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class GrassTuft(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_img('assets/textures/grass_tuft.png', (24, 16))
        self.rect = self.image.get_rect(midbottom=(x, y))

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class AlexNPC(pygame.sprite.Sprite):
    """Son leveldeki Alex."""
    def __init__(self, x, y):
        super().__init__()
        self.image = load_img('assets/textures/alex.png', (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.bob_timer = 0

    def update(self):
        self.bob_timer += 1

    def draw(self, surface, camera_x):
        yo = int(math.sin(self.bob_timer * 0.05) * 3)
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y + yo))
