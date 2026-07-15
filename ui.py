"""
ui.py - JustSteve v2
Can barı, zumrut, dokunmatik, olum ekrani, seviye gecis, Alex kurtarma sahnesi
"""
import pygame
import math
from settings import *
from sprites import load_img


class HUD:
    def __init__(self):
        self.heart_full = load_img('assets/textures/heart_full.png', (HEART_SIZE, HEART_SIZE))
        self.heart_empty = load_img('assets/textures/heart_empty.png', (HEART_SIZE, HEART_SIZE))
        self.emerald_icon = load_img('assets/textures/emerald_0.png', (EMERALD_ICON_SIZE, EMERALD_ICON_SIZE))
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 14, bold=True)
        # Skill ikonlari
        self.dj_icon = load_img('assets/textures/skill_doublejump.png', (20, 20))
        self.sh_icon = load_img('assets/textures/skill_shrink.png', (20, 20))

    def draw(self, surface, player, level_num, distance_ratio, biome_name=""):
        # Can bari
        for i in range(player.max_hp):
            img = self.heart_full if i < player.hp else self.heart_empty
            surface.blit(img, (10 + i * HEART_SPACING, 10))

        # Zumrut sayaci
        ex = WIDTH - 100
        surface.blit(self.emerald_icon, (ex, 12))
        self._txt(surface, f"x {player.emeralds}", ex + EMERALD_ICON_SIZE + 4, 12)

        # Seviye + biyom
        lt = f"Seviye {level_num + 1} - {biome_name}"
        tw = self.font.size(lt)[0]
        self._txt(surface, lt, WIDTH // 2 - tw // 2, 10)

        # Mesafe bari
        bw, bh = 200, 8
        bx, by = WIDTH // 2 - bw // 2, 35
        pygame.draw.rect(surface, (50, 50, 50), (bx, by, bw, bh), border_radius=4)
        fw = int(bw * min(distance_ratio, 1.0))
        if fw > 0:
            pygame.draw.rect(surface, (40, 200, 40), (bx, by, fw, bh), border_radius=4)
        pygame.draw.rect(surface, (100, 100, 100), (bx, by, bw, bh), 1, border_radius=4)

        # Aktif skill gostergesi
        sy = 42
        if player.has_double_jump:
            surface.blit(self.dj_icon, (10, sy))
        if player.is_shrunk:
            surface.blit(self.sh_icon, (34, sy))
            # Kalan sure
            secs = player.shrink_timer // FPS
            self._txt_small(surface, f"{secs}s", 56, sy + 3)

    def _txt(self, surface, text, x, y):
        shadow = self.font.render(text, True, (30, 30, 30))
        surface.blit(shadow, (x + 1, y + 1))
        txt = self.font.render(text, True, (255, 255, 255))
        surface.blit(txt, (x, y))

    def _txt_small(self, surface, text, x, y):
        txt = self.font_small.render(text, True, (255, 255, 255))
        surface.blit(txt, (x, y))


class TouchControls:
    def __init__(self):
        by = HEIGHT - TOUCH_BTN_SIZE - 15
        gap = 10
        self.btn_left = pygame.Rect(15, by, TOUCH_BTN_SIZE, TOUCH_BTN_SIZE)
        self.btn_right = pygame.Rect(15 + TOUCH_BTN_SIZE + gap, by, TOUCH_BTN_SIZE, TOUCH_BTN_SIZE)
        self.btn_jump = pygame.Rect(WIDTH - TOUCH_BTN_SIZE - 15, by, TOUCH_BTN_SIZE, TOUCH_BTN_SIZE)
        self.btn_dash = pygame.Rect(WIDTH - TOUCH_BTN_SIZE * 2 - 25, by, TOUCH_BTN_SIZE, TOUCH_BTN_SIZE)

        self.img_left = load_img('assets/ui/btn_left.png', (TOUCH_BTN_SIZE, TOUCH_BTN_SIZE))
        self.img_right = load_img('assets/ui/btn_right.png', (TOUCH_BTN_SIZE, TOUCH_BTN_SIZE))
        self.img_jump = load_img('assets/ui/btn_jump.png', (TOUCH_BTN_SIZE, TOUCH_BTN_SIZE))
        self.img_dash = load_img('assets/ui/btn_dash.png', (TOUCH_BTN_SIZE, TOUCH_BTN_SIZE))

        self.pressing_left = False
        self.pressing_right = False
        self.pressing_jump = False
        self.pressing_dash = False

    def handle_event(self, event, player):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = event.pos if hasattr(event, 'pos') else (int(event.x * WIDTH), int(event.y * HEIGHT))
            if self.btn_left.collidepoint(pos): self.pressing_left = True
            if self.btn_right.collidepoint(pos): self.pressing_right = True
            if self.btn_jump.collidepoint(pos):
                self.pressing_jump = True
                player.request_jump()
            if self.btn_dash.collidepoint(pos):
                self.pressing_dash = True
                player.start_dash()
        elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            self.pressing_left = False
            self.pressing_right = False
            if self.pressing_jump:
                self.pressing_jump = False
                player.release_jump()
            self.pressing_dash = False

    def get_move_x(self):
        mx = 0
        if self.pressing_left: mx -= 1
        if self.pressing_right: mx += 1
        return mx

    def draw(self, surface):
        for img, rect in [(self.img_left, self.btn_left), (self.img_right, self.btn_right),
                          (self.img_jump, self.btn_jump), (self.img_dash, self.btn_dash)]:
            tmp = img.copy(); tmp.set_alpha(TOUCH_BTN_ALPHA)
            surface.blit(tmp, rect)


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.bg_img = load_img('assets/ui/button.png', (width, height))
        self.font = pygame.font.SysFont('Arial', 22, bold=True)

    def draw(self, surface):
        img = self.bg_img.copy()
        if self.hovered:
            bright = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            bright.fill((255, 255, 255, 40))
            img.blit(bright, (0, 0))
        surface.blit(img, self.rect)
        shadow = self.font.render(self.text, True, (30, 30, 30))
        surface.blit(shadow, shadow.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2)))
        txt = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


class DeathScreen:
    def __init__(self, on_restart):
        self.font_big = pygame.font.SysFont('Arial', 52, bold=True)
        self.restart_btn = Button(WIDTH // 2 - 110, HEIGHT // 2 + 20, 220, 50, "Tekrar Oyna", on_restart)
        self.alpha = 0

    def handle_event(self, event):
        self.restart_btn.handle_event(event)

    def draw(self, surface):
        if self.alpha < 180: self.alpha += 3
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, self.alpha))
        surface.blit(ov, (0, 0))
        txt = self.font_big.render("Oldun!", True, (220, 40, 40))
        shadow = self.font_big.render("Oldun!", True, (60, 10, 10))
        cx = WIDTH // 2 - txt.get_width() // 2
        surface.blit(shadow, (cx + 3, HEIGHT // 3 + 3))
        surface.blit(txt, (cx, HEIGHT // 3))
        self.restart_btn.draw(surface)


class LevelCompleteScreen:
    def __init__(self, level_num, on_next, on_menu):
        self.font_big = pygame.font.SysFont('Arial', 44, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 20)
        self.alpha = 0
        self.is_final = level_num >= 4

        if self.is_final:
            self.title = "Alex Kurtarildi!"
            self.btn = Button(WIDTH // 2 - 110, HEIGHT // 2 + 60, 220, 50, "Ana Menu", on_menu)
        else:
            self.title = f"Seviye {level_num + 1} Tamamlandi!"
            self.btn = Button(WIDTH // 2 - 110, HEIGHT // 2 + 60, 220, 50, "Sonraki Seviye", on_next)

        # Alex kurtarma animasyonu
        self.cutscene_timer = 0

    def handle_event(self, event):
        self.btn.handle_event(event)

    def draw(self, surface):
        if self.alpha < 160: self.alpha += 2
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, self.alpha))
        surface.blit(ov, (0, 0))

        self.cutscene_timer += 1

        if self.is_final:
            # Alex kurtarma sahnesi animasyonu
            self._draw_rescue_cutscene(surface)
        else:
            txt = self.font_big.render(self.title, True, (40, 220, 40))
            shadow = self.font_big.render(self.title, True, (10, 60, 10))
            cx = WIDTH // 2 - txt.get_width() // 2
            surface.blit(shadow, (cx + 3, HEIGHT // 3 + 3))
            surface.blit(txt, (cx, HEIGHT // 3))

        self.btn.draw(surface)

    def _draw_rescue_cutscene(self, surface):
        """Alex kurtarma sahnesi - Steve ve Alex bulusuyor."""
        font_big = self.font_big
        font_med = self.font_med

        # Baslik
        title_alpha = min(255, self.cutscene_timer * 4)
        title_surf = font_big.render("Alex Kurtarildi!", True, (255, 220, 50))
        title_surf.set_alpha(title_alpha)
        cx = WIDTH // 2 - title_surf.get_width() // 2
        surface.blit(title_surf, (cx, HEIGHT // 5))

        # Steve ve Alex yaklasma animasyonu
        steve_img = load_img('assets/textures/steve_idle_0.png', (PLAYER_WIDTH, PLAYER_HEIGHT))
        alex_img = load_img('assets/textures/alex.png', (PLAYER_WIDTH, PLAYER_HEIGHT))

        center_x = WIDTH // 2
        center_y = HEIGHT // 2 - 20
        max_offset = 100
        approach = min(self.cutscene_timer * 1.2, max_offset)

        steve_x = center_x - approach  # Steve soldan gelir -> ortaya
        alex_x = center_x + approach   # Alex sagdan -> ortaya

        # Eger yakin geldilerse, ikisi yanyana dur
        if approach >= max_offset:
            steve_x = center_x - 20
            alex_x = center_x + 20

        surface.blit(steve_img, (int(steve_x) - PLAYER_WIDTH // 2, center_y))
        surface.blit(alex_img, (int(alex_x) - PLAYER_WIDTH // 2, center_y))

        # Kalp animasyonu (yakin gelince)
        if approach >= max_offset:
            heart_img = load_img('assets/textures/heart_full.png', (20, 20))
            bob = int(math.sin(self.cutscene_timer * 0.08) * 5)
            surface.blit(heart_img, (center_x - 10, center_y - 25 + bob))

            # Alt metin
            if self.cutscene_timer > 120:
                sub = font_med.render("Birlikte portaldan geciyorlar...", True, (200, 200, 200))
                sub_alpha = min(255, (self.cutscene_timer - 120) * 3)
                sub.set_alpha(sub_alpha)
                surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, center_y + PLAYER_HEIGHT + 20))
