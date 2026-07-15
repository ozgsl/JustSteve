"""
level.py - JustSteve v2
Biyom sistemi, prosedural uretim, portal, dekorasyon, Alex
"""
import pygame
import random
import math
from settings import *
from sprites import (
    Block, QuestionBlock, Player, Zombie, Skeleton, Enderman, Creeper,
    Emerald, HeartPickup, SkillDrop, Arrow, Explosion, Particle,
    Portal, Cloud, TreeDecor, GrassTuft, AlexNPC, Trader, Llama
)


class Level:
    def __init__(self, level_num, surface):
        self.display_surface = surface
        self.level_num = level_num
        self.biome = BIOMES[level_num]

        gap_r, enemy_r, speed_m = LEVEL_DIFFICULTY[level_num]
        self.gap_chance = gap_r
        self.enemy_chance = enemy_r
        self.speed_mult = speed_m
        self.target_distance = LEVEL_DISTANCES[level_num]

        # Kamera
        self.camera_x = 0

        # Sprite gruplari
        self.blocks = pygame.sprite.Group()
        self.question_blocks = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.arrows = pygame.sprite.Group()
        self.emeralds = pygame.sprite.Group()
        self.hearts = pygame.sprite.Group()
        self.skill_drops = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.traders = pygame.sprite.Group()
        self.llamas = pygame.sprite.Group()

        # Dekorasyon
        self.clouds = []
        self.trees = []
        self.grass_tufts = []

        # Portal (seviye sonunda olusturulacak)
        self.portal = None
        self.portal_spawned = False

        # Alex (sadece son seviye)
        self.alex = None

        # Oyuncu
        self.player = Player(100, GROUND_ROW * TILE_SIZE - PLAYER_HEIGHT - 5)
        self.player_group.add(self.player)

        # Prosedural uretim
        self.generated_up_to = 0
        self.chunk_index = 0
        self.decor_generated_up_to = 0

        # Ses
        self.coin_sound = self._snd('assets/sounds/coin.ogg')
        if self.coin_sound: self.coin_sound.set_volume(1.0)
        self.stomp_sound = self._snd('assets/sounds/stomp.ogg')

        # Ilk uretim
        self._generate_until(WIDTH + CHUNK_WIDTH * 3)
        self._generate_decor_until(WIDTH + CHUNK_WIDTH * 3)
        self._generate_clouds()

        # Durum
        self.completed = False
        self.player_dead = False
        self.portal_entered = False

    def _snd(self, p):
        try: return pygame.mixer.Sound(p)
        except: return None

    # ------- Gokyuzu & Bulutlar -------
    def _generate_clouds(self):
        cc = self.biome.get('cloud_color', (255, 255, 255))
        for _ in range(12):
            x = random.randint(-200, int(self.target_distance * 0.4))
            y = random.randint(20, 120)
            self.clouds.append(Cloud(x, y, cc))

    def _draw_background(self):
        st = self.biome['sky_top']
        sb = self.biome['sky_bottom']
        for y in range(0, HEIGHT, 2):  # 2 piksel adim (performans)
            r = y / HEIGHT
            c = (int(st[0]*(1-r)+sb[0]*r), int(st[1]*(1-r)+sb[1]*r), int(st[2]*(1-r)+sb[2]*r))
            pygame.draw.line(self.display_surface, c, (0, y), (WIDTH, y))
            pygame.draw.line(self.display_surface, c, (0, y+1), (WIDTH, y+1))

        # Gunes
        sun_x = WIDTH - 80 - self.camera_x * 0.02
        pygame.draw.circle(self.display_surface, (255, 240, 100), (int(sun_x), 60), 30)
        pygame.draw.circle(self.display_surface, (255, 250, 180, 60), (int(sun_x), 60), 40)

        # Bulutlar
        for cloud in self.clouds:
            cloud.draw(self.display_surface, self.camera_x)

    # ------- Dekorasyon uretimi -------
    def _generate_decor_until(self, world_x):
        tree_type = self.biome.get('tree')
        while self.decor_generated_up_to < world_x:
            bx = self.decor_generated_up_to
            # Agac
            if tree_type and random.random() < 0.12:
                tx = bx + random.randint(0, CHUNK_WIDTH)
                ty = GROUND_ROW * TILE_SIZE
                self.trees.append(TreeDecor(tx, ty, tree_type))
            # Cim tutami
            if random.random() < 0.3:
                for _ in range(random.randint(1, 3)):
                    gx = bx + random.randint(0, CHUNK_WIDTH)
                    gy = GROUND_ROW * TILE_SIZE
                    self.grass_tufts.append(GrassTuft(gx, gy))
            self.decor_generated_up_to += CHUNK_WIDTH

    # ------- Chunk uretimi -------
    def _generate_until(self, world_x):
        while self.generated_up_to < world_x:
            self._generate_chunk(self.generated_up_to, self.chunk_index)
            self.generated_up_to += CHUNK_WIDTH
            self.chunk_index += 1

    def _generate_chunk(self, start_x, chunk_idx):
        biome = self.biome
        is_safe = chunk_idx < 3

        # Portal mesafesine ulasildi mi?
        if start_x >= self.target_distance and not self.portal_spawned:
            self._spawn_portal(start_x)
            return

        # Bosluk
        has_gap = False; gap_start = -1; gap_end = -1
        if not is_safe and random.random() < self.gap_chance:
            has_gap = True
            gap_start = random.randint(3, CHUNK_COLS - 5)
            gap_end = min(gap_start + random.randint(2, 3), CHUNK_COLS - 2)

        # Platform
        has_plat = False; plat_s = -1; plat_e = -1; plat_row = GROUND_ROW
        if not is_safe and random.random() < 0.55:
            has_plat = True
            plat_s = random.randint(2, CHUNK_COLS - 6)
            plat_e = plat_s + random.randint(3, 5)
            plat_row = GROUND_ROW - random.randint(3, 6)
            # Bosluk olmayan yerde platform (gecis sagla)
            # Platform min 2 tile yukseklikte olsun ki oyuncu gecebilsin
            if plat_row > GROUND_ROW - 2:
                plat_row = GROUND_ROW - 3

        # Zemin bloklari
        ground_img = f'assets/textures/{biome["ground"]}.png'
        under_img = f'assets/textures/{biome["under"]}.png'
        plat_img = f'assets/textures/{biome["platform"]}.png'

        for col in range(CHUNK_COLS):
            wx = start_x + col * TILE_SIZE
            if has_gap and gap_start <= col < gap_end:
                continue
            self.blocks.add(Block(wx, GROUND_ROW * TILE_SIZE, ground_img))
            for row in range(GROUND_ROW + 1, TOTAL_ROWS):
                self.blocks.add(Block(wx, row * TILE_SIZE, under_img))

        # Platform
        if has_plat:
            for col in range(plat_s, min(plat_e, CHUNK_COLS)):
                wx = start_x + col * TILE_SIZE
                self.blocks.add(Block(wx, plat_row * TILE_SIZE, plat_img))

        # Soru blogu
        if not is_safe and random.random() < 0.25:
            qc = random.randint(2, CHUNK_COLS - 3)
            qr = GROUND_ROW - random.randint(3, 5)
            if not (has_gap and gap_start <= qc < gap_end):
                self.question_blocks.add(QuestionBlock(start_x + qc * TILE_SIZE, qr * TILE_SIZE))

        # Dusman
        if not is_safe and random.random() < self.enemy_chance:
            ec = random.randint(3, CHUNK_COLS - 3)
            if not (has_gap and gap_start <= ec < gap_end):
                ex = start_x + ec * TILE_SIZE
                ey = GROUND_ROW * TILE_SIZE - PLAYER_HEIGHT
                etype = self._pick_enemy()
                enemy = etype(ex, ey, self.speed_mult)
                enemy.player_ref = self.player
                self.enemies.add(enemy)

        # Zumrut
        if not is_safe and random.random() < 0.2:
            for _ in range(random.randint(1, 3)):
                ec2 = random.randint(1, CHUNK_COLS - 2)
                if not (has_gap and gap_start <= ec2 < gap_end):
                    self.emeralds.add(Emerald(
                        start_x + ec2 * TILE_SIZE + TILE_SIZE // 2,
                        (GROUND_ROW - random.randint(2, 4)) * TILE_SIZE + TILE_SIZE // 2
                    ))

        # Trader & Llama
        if not is_safe and random.random() < 0.05:
            tc = random.randint(2, CHUNK_COLS - 3)
            if not (has_gap and gap_start <= tc < gap_end):
                tx = start_x + tc * TILE_SIZE
                ty = GROUND_ROW * TILE_SIZE
                self.traders.add(Trader(tx, ty))
                self.llamas.add(Llama(tx + 45, ty))

    def _spawn_portal(self, x):
        self.portal_spawned = True
        # Duz zemin olustur
        ground_img = f'assets/textures/{self.biome["ground"]}.png'
        under_img = f'assets/textures/{self.biome["under"]}.png'
        for col in range(CHUNK_COLS * 2):
            wx = x + col * TILE_SIZE
            self.blocks.add(Block(wx, GROUND_ROW * TILE_SIZE, ground_img))
            for row in range(GROUND_ROW + 1, TOTAL_ROWS):
                self.blocks.add(Block(wx, row * TILE_SIZE, under_img))

        px = x + CHUNK_WIDTH
        py = GROUND_ROW * TILE_SIZE
        self.portal = Portal(px, py)

        # Son seviyede Alex
        if self.level_num >= 4:
            self.alex = AlexNPC(px - 60, py)

    def _pick_enemy(self):
        if self.level_num == 0: return Zombie
        elif self.level_num == 1: return random.choice([Zombie, Zombie, Skeleton])
        elif self.level_num == 2: return random.choice([Zombie, Skeleton, Enderman])
        elif self.level_num == 3: return random.choice([Zombie, Skeleton, Enderman, Creeper])
        else: return random.choice([Zombie, Skeleton, Skeleton, Enderman, Creeper])

    # ------- Temizlik -------
    def _cleanup_left(self):
        thresh = self.camera_x - CHUNK_WIDTH * 2
        for grp in [self.blocks, self.question_blocks, self.enemies,
                     self.emeralds, self.arrows, self.skill_drops,
                     self.traders, self.llamas]:
            for s in list(grp):
                if s.rect.right < thresh: s.kill()
        self.trees = [t for t in self.trees if t.rect.right > thresh]
        self.grass_tufts = [g for g in self.grass_tufts if g.rect.right > thresh]

    # ------- Kamera -------
    def _update_camera(self):
        target = self.player.rect.centerx - WIDTH // 3
        self.camera_x += (target - self.camera_x) * 0.1
        if self.camera_x < 0: self.camera_x = 0

    # ------- Carpisma -------
    def _horizontal_collisions(self):
        p = self.player
        p.rect.x += p.vel.x
        for b in list(self.blocks) + list(self.question_blocks):
            if b.rect.colliderect(p.rect):
                if p.vel.x > 0: p.rect.right = b.rect.left
                elif p.vel.x < 0: p.rect.left = b.rect.right

    def _vertical_collisions(self):
        p = self.player
        p.apply_gravity()
        p.rect.y += p.vel.y
        p.on_ground = False

        for b in list(self.blocks) + list(self.question_blocks):
            if b.rect.colliderect(p.rect):
                if p.vel.y > 0:
                    p.rect.bottom = b.rect.top
                    p.vel.y = 0
                    p.on_ground = True
                elif p.vel.y < 0:
                    p.rect.top = b.rect.bottom
                    p.vel.y = 0
                    if isinstance(b, QuestionBlock) and b.hit():
                        self.emeralds.add(Emerald(b.rect.centerx, b.rect.top - 10, True))
                        if self.coin_sound: self.coin_sound.play()

    def _enemy_block_collisions(self):
        for enemy in self.enemies:
            if not enemy.alive: continue
            for b in self.blocks:
                if enemy.rect.colliderect(b.rect):
                    if enemy.vel_y >= 0 and enemy.rect.bottom > b.rect.top and enemy.rect.top < b.rect.top:
                        enemy.rect.bottom = b.rect.top
                        enemy.vel_y = 0
                        enemy.on_ground = True
                    elif abs(enemy.rect.right - b.rect.left) < 10 and enemy.direction > 0:
                        enemy.direction *= -1
                    elif abs(enemy.rect.left - b.rect.right) < 10 and enemy.direction < 0:
                        enemy.direction *= -1

    def _enemy_collisions(self):
        p = self.player
        if not p.alive: return

        for enemy in list(self.enemies):
            if not enemy.alive: continue
            # Creeper patlama kontrolu
            if isinstance(enemy, Creeper) and enemy.exploded:
                exp = Explosion(enemy.rect.centerx, enemy.rect.centery)
                self.explosions.add(exp)
                # Alan hasari
                dist = math.hypot(p.rect.centerx - enemy.rect.centerx,
                                  p.rect.centery - enemy.rect.centery)
                if dist < CREEPER_EXPLODE_RADIUS:
                    p.take_damage(2)
                # Parcaciklar
                for _ in range(12):
                    self.particles.add(Particle(enemy.rect.centerx, enemy.rect.centery,
                                                color=(255, 140, 30)))
                # Skill drop
                self._drop_skill(enemy)
                if enemy.drops_heart:
                    self.hearts.add(HeartPickup(enemy.rect.centerx, enemy.rect.top))
                enemy.kill()
                continue

            if enemy.rect.colliderect(p.rect):
                if p.vel.y > 0 and p.rect.bottom < enemy.rect.centery + 10:
                    killed = enemy.take_hit()
                    if p.jump_held:
                        p.vel.y = JUMP_FORCE * 0.9 # High bounce
                    else:
                        p.vel.y = JUMP_FORCE * 0.5 # Short hop
                    
                    if self.stomp_sound: self.stomp_sound.play()
                    if killed:
                        for _ in range(8):
                            self.particles.add(Particle(enemy.rect.centerx, enemy.rect.centery,
                                                        color=(100, 200, 100)))
                        if enemy.drops_heart:
                            self.hearts.add(HeartPickup(enemy.rect.centerx, enemy.rect.top))
                        self._drop_skill(enemy)
                else:
                    p.take_damage()

    def _drop_skill(self, enemy):
        """Mob oldugunde skill drop sansi."""
        roll = random.random()
        if roll < 0.15:
            self.skill_drops.add(SkillDrop(enemy.rect.centerx, enemy.rect.top, 'doublejump'))
        elif roll < 0.25:
            self.skill_drops.add(SkillDrop(enemy.rect.centerx, enemy.rect.top, 'shrink'))

    def _item_collisions(self):
        p = self.player
        if not p.alive: return

        for em in list(self.emeralds):
            if em.rect.colliderect(p.rect):
                em.kill(); p.emeralds += 1
                if self.coin_sound: self.coin_sound.play()
                for _ in range(4):
                    self.particles.add(Particle(em.rect.centerx, em.rect.centery, color=(40, 200, 40)))

        for h in list(self.hearts):
            if h.rect.colliderect(p.rect):
                h.kill(); p.heal(1)

        for sd in list(self.skill_drops):
            if sd.rect.colliderect(p.rect):
                if sd.skill_type == 'doublejump':
                    p.activate_double_jump()
                elif sd.skill_type == 'shrink':
                    p.activate_shrink()
                elif sd.skill_type in ['bow', 'sword', 'shield']:
                    p.activate_trader_skill(sd.skill_type)
                sd.kill()
                for _ in range(6):
                    self.particles.add(Particle(sd.rect.centerx, sd.rect.centery, color=(200, 100, 255)))

        # Trader Ticareti
        for trader in pygame.sprite.spritecollide(p, self.traders, False):
            if not trader.traded and p.emeralds >= TRADER_SKILL_COST:
                p.emeralds -= TRADER_SKILL_COST
                trader.traded = True
                if self.coin_sound: self.coin_sound.play()
                # Skill drop
                stype = random.choice(['bow', 'sword', 'shield'])
                self.skill_drops.add(SkillDrop(trader.rect.centerx, trader.rect.top - 20, stype))

        # Skill drop block carpismasi (yere dussun)
        for sd in self.skill_drops:
            for b in self.blocks:
                if sd.rect.colliderect(b.rect) and sd.vel_y > 0:
                    sd.rect.bottom = b.rect.top
                    sd.vel_y = 0
                    break

        # Heart block carpismasi
        for h in self.hearts:
            for b in self.blocks:
                if h.rect.colliderect(b.rect) and h.vel_y > 0:
                    h.rect.bottom = b.rect.top
                    h.vel_y = 0
                    break

        # Ok hasari
        for arrow in list(self.arrows):
            if arrow.is_player_arrow:
                for e in list(self.enemies):
                    if arrow.rect.colliderect(e.rect):
                        arrow.kill()
                        e.kill()
                        self._create_explosion(e.rect.centerx, e.rect.centery)
                        break
            else:
                if arrow.rect.colliderect(p.rect):
                    arrow.kill(); p.take_damage()

        # Portal kontrolu (ustunden atlamayi engellemek icin X koordinatini kontrol et)
        if self.portal and p.rect.centerx >= self.portal.rect.centerx:
            self.portal_entered = True
            self.completed = True

    def _check_death(self):
        if self.player.rect.top > KILL_Y:
            self.player.alive = False
            self.player_dead = True
        elif not self.player.alive:
            self.player_dead = True

    # ------- Ana update -------
    def update(self, move_x):
        if not self.player.alive:
            self.player_dead = True
            return

        p = self.player
        if p.dashing:
            p.vel.x = DASH_SPEED * p.dash_dir
        else:
            if move_x != 0:
                if (move_x > 0 and p.vel.x < 0) or (move_x < 0 and p.vel.x > 0):
                    p.vel.x += move_x * SKID_FRICTION
                else:
                    p.vel.x += move_x * ACCELERATION
                
                if abs(p.vel.x) > MAX_SPEED:
                    p.vel.x = MAX_SPEED if p.vel.x > 0 else -MAX_SPEED
            else:
                if p.vel.x > 0:
                    p.vel.x = max(0, p.vel.x - FRICTION)
                elif p.vel.x < 0:
                    p.vel.x = min(0, p.vel.x + FRICTION)
                    
        if move_x > 0: p.facing_right = True
        elif move_x < 0: p.facing_right = False

        self._horizontal_collisions()
        self._vertical_collisions()
        self._enemy_block_collisions()
        self._enemy_collisions()
        self._item_collisions()
        self._check_death()

        self._update_camera()
        self._generate_until(self.camera_x + WIDTH + CHUNK_WIDTH * 3)
        self._generate_decor_until(self.camera_x + WIDTH + CHUNK_WIDTH * 3)
        self._cleanup_left()

        p.world_x = max(p.world_x, p.rect.centerx + self.camera_x)
        
        # Oyuncu saldirisi
        attack = self.player.do_attack()
        if attack == 'bow':
            dir = 1 if self.player.facing_right else -1
            self.arrows.add(Arrow(self.player.rect.centerx, self.player.rect.centery, dir, is_player_arrow=True))
        elif attack == 'sword':
            dir = 1 if self.player.facing_right else -1
            hitbox = pygame.Rect(self.player.rect.centerx + (20 * dir) - 30, self.player.rect.centery - 30, 60, 60)
            for e in list(self.enemies):
                if hitbox.colliderect(e.rect):
                    e.kill()
                    self._create_explosion(e.rect.centerx, e.rect.centery)
                    
        # Gruplari guncelle
        self.player_group.update()
        self.enemies.update()
        self.arrows.update()
        self.question_blocks.update()
        self.emeralds.update()
        self.hearts.update()
        self.skill_drops.update()
        self.particles.update()
        self.explosions.update()
        if self.alex: self.alex.update()
        self.traders.update()
        self.llamas.update()
        if self.alex: self.alex.update()

        # Iskelet oklari
        for e in self.enemies:
            if isinstance(e, Skeleton):
                e.arrows.update()
                for a in e.arrows: self.arrows.add(a)
        self.arrows.update()

    # ------- Cizim -------
    def draw(self):
        self._draw_background()
        cx = int(self.camera_x)

        # Agaclar (arka plan)
        for t in self.trees:
            t.draw(self.display_surface, cx)

        # Cim
        for g in self.grass_tufts:
            g.draw(self.display_surface, cx)

        # Bloklar
        for b in self.blocks:
            self.display_surface.blit(b.image, (b.rect.x - cx, b.rect.y))

        # Soru bloklari
        for qb in self.question_blocks:
            qb.draw_offset(self.display_surface, cx)

        # Portal
        if self.portal:
            self.display_surface.blit(self.portal.image, (self.portal.rect.x - cx, self.portal.rect.y))

        # Zumrutler
        for em in self.emeralds:
            self.display_surface.blit(em.image, (em.rect.x - cx, em.rect.y))

        # Kalpler & Skill droplar
        for h in self.hearts: self.display_surface.blit(h.image, (h.rect.x - cx, h.rect.y))
        for sd in self.skill_drops: self.display_surface.blit(sd.image, (sd.rect.x - cx, sd.rect.y))
        for p in self.particles: self.display_surface.blit(p.image, (p.rect.x - cx, p.rect.y))
        for ex in self.explosions: self.display_surface.blit(ex.image, (ex.rect.x - cx, ex.rect.y))
        for tr in self.traders: self.display_surface.blit(tr.image, (tr.rect.x - cx, tr.rect.y))
        for ll in self.llamas: self.display_surface.blit(ll.image, (ll.rect.x - cx, ll.rect.y))
        if self.player.alive:
            self.display_surface.blit(self.player.image, (self.player.rect.x - cx, self.player.rect.y))
        
        # Dusmanlar
        for e in self.enemies:
            self.display_surface.blit(e.image, (e.rect.x - cx, e.rect.y))

        # Oklar
        for a in self.arrows:
            self.display_surface.blit(a.image, (a.rect.x - cx, a.rect.y))

        if self.alex: self.alex.draw(self.display_surface, cx)
