"""
main.py - JustSteve v2
Biyom gecisleri, portal animasyonu, Alex kurtarma sahnesi
"""
import pygame
import sys
from settings import *
from level import Level
from ui import HUD, TouchControls, Button, DeathScreen, LevelCompleteScreen


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("JustSteve")
        self.clock = pygame.time.Clock()

        self.state = "MENU"
        self.current_level = 0

        # Muzik
        self.music_on = True
        self._play_music('assets/sounds/music_menu.ogg')

    def _play_music(self, path):
        if not self.music_on: return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        # UI
        self.hud = HUD()
        self.touch = TouchControls()
        self.death_screen = None
        self.complete_screen = None
        self.level = None

        # Portal gecis efekti
        self.transition_alpha = 0
        self.transitioning = False
        self.transition_callback = None

        # Font
        self.font_title = pygame.font.SysFont('Arial', 56, bold=True)
        self.font_sub = pygame.font.SysFont('Arial', 18)

        self._setup_menu()

    def _setup_menu(self):
        bw, bh = 220, 50
        cx = WIDTH // 2 - bw // 2
        self.menu_buttons = [
            Button(cx, HEIGHT // 2 - 30, bw, bh, "Oyna", self._start_game),
            Button(cx, HEIGHT // 2 + 35, bw, bh,
                   "Muzik: Acik" if self.music_on else "Muzik: Kapali",
                   self._toggle_music),
            Button(cx, HEIGHT // 2 + 100, bw, bh, "Cikis", self._quit),
        ]

    def _start_game(self):
        self.current_level = 0
        self._play_music('assets/sounds/music_game.ogg')
        self._start_transition(self._load_level)

    def _load_level(self):
        self.level = Level(self.current_level, self.screen)
        self.death_screen = None
        self.complete_screen = None
        self.state = "PLAYING"

    def _next_level(self):
        self.current_level += 1
        if self.current_level >= 5:
            self._start_transition(self._go_menu)
        else:
            self._start_transition(self._load_level)

    def _go_menu(self):
        self.state = "MENU"
        self._play_music('assets/sounds/music_menu.ogg')
        self._setup_menu()

    def _toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.menu_buttons[1].text = "Muzik: Acik" if self.music_on else "Muzik: Kapali"

    def _quit(self):
        pygame.quit()
        sys.exit()

    def _on_death(self):
        self._start_transition(self._go_menu)

    def _start_transition(self, callback):
        """Portal gecis efekti baslat (ekran kararir -> callback -> ekran acilir)."""
        self.transitioning = True
        self.transition_alpha = 0
        self.transition_callback = callback
        self.transition_phase = 'fade_out'  # fade_out -> callback -> fade_in

    def _update_transition(self):
        if not self.transitioning:
            return
        if self.transition_phase == 'fade_out':
            self.transition_alpha += 8
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                if self.transition_callback:
                    self.transition_callback()
                self.transition_phase = 'fade_in'
        elif self.transition_phase == 'fade_in':
            self.transition_alpha -= 5
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transitioning = False

    def _draw_transition(self):
        if self.transitioning and self.transition_alpha > 0:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            # Portal mor tonu
            ov.fill((40, 10, 80, self.transition_alpha))
            self.screen.blit(ov, (0, 0))

    def _text_c(self, text, font, color, y, shadow=True):
        if shadow:
            s = font.render(text, True, (30, 30, 30))
            self.screen.blit(s, s.get_rect(center=(WIDTH // 2 + 2, y + 2)))
        t = font.render(text, True, color)
        self.screen.blit(t, t.get_rect(center=(WIDTH // 2, y)))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()

                if self.transitioning:
                    continue  # Gecis sirasinda girdi alma

                if self.state == "MENU":
                    for btn in self.menu_buttons:
                        btn.handle_event(event)
                elif self.state == "PLAYING":
                    self.touch.handle_event(event, self.level.player)
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                            self.level.player.request_jump()
                        if event.key in (pygame.K_LSHIFT, pygame.K_z):
                            self.level.player.start_dash()
                    if event.type == pygame.KEYUP:
                        if event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                            self.level.player.release_jump()
                elif self.state == "DEAD":
                    if self.death_screen:
                        self.death_screen.handle_event(event)
                elif self.state == "LEVEL_COMPLETE":
                    if self.complete_screen:
                        self.complete_screen.handle_event(event)

            # -- Guncelleme --
            self._update_transition()

            if self.state == "PLAYING" and not self.transitioning:
                keys = pygame.key.get_pressed()
                kb = 0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: kb -= 1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: kb += 1
                tm = self.touch.get_move_x()
                mx = kb if kb != 0 else tm

                self.level.update(mx)

                if self.level.player_dead:
                    self.state = "DEAD"
                    self.death_screen = DeathScreen(self._on_death)
                elif self.level.completed:
                    self.state = "LEVEL_COMPLETE"
                    self.complete_screen = LevelCompleteScreen(
                        self.current_level, self._next_level, self._go_menu
                    )

            # -- Cizim --
            self.screen.fill((0, 0, 0))

            if self.state == "MENU":
                # Gradient arka plan
                for y in range(0, HEIGHT, 2):
                    r = y / HEIGHT
                    c = (int(80*(1-r)+30*r), int(120*(1-r)+50*r), int(200*(1-r)+80*r))
                    pygame.draw.line(self.screen, c, (0, y), (WIDTH, y))
                    pygame.draw.line(self.screen, c, (0, y+1), (WIDTH, y+1))
                self._text_c("JustSteve", self.font_title, (255, 255, 255), HEIGHT // 4)
                self._text_c("Alex'i Kurtar!", self.font_sub, (200, 200, 200), HEIGHT // 4 + 50)
                for btn in self.menu_buttons:
                    btn.draw(self.screen)

            elif self.state in ("PLAYING", "DEAD", "LEVEL_COMPLETE"):
                self.level.draw()
                biome_name = BIOMES[self.current_level].get('name', '')
                dr = self.level.player.world_x / self.level.target_distance
                self.hud.draw(self.screen, self.level.player, self.current_level, dr, biome_name)

                if self.state == "PLAYING":
                    self.touch.draw(self.screen)
                elif self.state == "DEAD" and self.death_screen:
                    self.death_screen.draw(self.screen)
                elif self.state == "LEVEL_COMPLETE" and self.complete_screen:
                    self.complete_screen.draw(self.screen)

            # Gecis efekti (en uste)
            self._draw_transition()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
