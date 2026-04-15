import pygame
import sys
import math
import random
from collections import deque

pygame.init()

# =========================================================
# 기본 설정
# =========================================================
TILE_SIZE = 32
FPS = 60

MAP_W = 30
MAP_H = 18

WIDTH = TILE_SIZE * MAP_W
UI_HEIGHT = 140
GAME_HEIGHT = TILE_SIZE * MAP_H
HEIGHT = GAME_HEIGHT + UI_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Worm RPG Prototype - Infinite Rooms")
clock = pygame.time.Clock()


def get_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        f = pygame.font.SysFont(name, size)
        if f.get_ascent() > 0:
            return f
    return pygame.font.SysFont(None, size)


font = get_font(24)
small_font = get_font(18)
big_font = get_font(44)

# =========================================================
# 색상
# =========================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (85, 85, 85)
DARK_GRAY = (45, 45, 45)
GREEN = (60, 200, 60)
RED = (220, 70, 70)
BLUE = (80, 120, 240)
YELLOW = (255, 220, 80)
PURPLE = (180, 70, 220)
BROWN = (130, 90, 50)
CYAN = (80, 220, 240)
ORANGE = (255, 150, 50)
BEIGE = (160, 140, 90)

# =========================================================
# 방향
# =========================================================
MOVE_DIRS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}

# 월드 좌표용
ROOM_DIRS = {
    "up": (0, 1),
    "down": (0, -1),
    "left": (-1, 0),
    "right": (1, 0),
}

# =========================================================
# 직업 데이터
# =========================================================
CLASS_DATA = {
    "warrior": {
        "name": "전사",
        "max_hp": 100,
        "max_mp": 30,
        "hp_regen": 0.6,
        "mp_regen": 0.6,
        "intelligence": 0,
        "vitality": 5,
        "muscle": 5,
    },
    "mage": {
        "name": "마법사",
        "max_hp": 40,
        "max_mp": 100,
        "hp_regen": 0.2,
        "mp_regen": 2.4,
        "intelligence": 5,
        "vitality": 2,
        "muscle": 0,
    },
}

# =========================================================
# 이미지 로드
# =========================================================
TILE_1_PATH = "C:/Users/fande/OneDrive/바탕 화면/school folder/AIgames1/game_1/Game_image/tile_1.png"

try:
    tile_1_img = pygame.image.load(TILE_1_PATH).convert_alpha()
    tile_1_img = pygame.transform.scale(tile_1_img, (TILE_SIZE, TILE_SIZE))
except Exception as e:
    print(f"tile_1.png 로드 실패: {e}")
    tile_1_img = None

# =========================================================
# 방 템플릿
# =========================================================
ROOM_CENTER = [
    "000000000000002220000000000000",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "222111111111111111111111111222",
    "111111111111111111111111111111",
    "111111111111111111111111111111",
    "111111111111111111111111111111",
    "111111111111111111111111111111",
    "111111111111111111111111111111",
    "222111111111111111111111111222",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "000000000000001110000000000000",
    "000000000000002220000000000000",
]

ROOM_X = [
    "000000000000002220000000000000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
]

ROOM_Y = [
    "000000000000002220000000000000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000000000000002220000000000000",
]

ROOM_X_VARIANTS = [ROOM_X]
ROOM_Y_VARIANTS = [ROOM_Y]
ROOM_CENTER_VARIANTS = [ROOM_CENTER]

# =========================================================
# 유틸
# =========================================================
def tile_rect(tx, ty):
    return pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def draw_hex_frame(surface, center, radius, color, width=3):
    cx, cy = center
    points = [
        (cx, cy - radius),
        (cx + radius * 0.87, cy - radius * 0.5),
        (cx + radius * 0.87, cy + radius * 0.5),
        (cx, cy + radius),
        (cx - radius * 0.87, cy + radius * 0.5),
        (cx - radius * 0.87, cy - radius * 0.5),
    ]
    pygame.draw.polygon(surface, color, points, width)


# =========================================================
# 방 생성
# =========================================================
def generate_room_by_exit(exit_dir):
    if exit_dir in ("left", "right"):
        return random.choice(ROOM_X_VARIANTS)
    if exit_dir in ("up", "down"):
        return random.choice(ROOM_Y_VARIANTS)
    return random.choice(ROOM_CENTER_VARIANTS)


# =========================================================
# Infinite Map Manager
# =========================================================
class MapManager:
    def __init__(self, start_room=(0, 0)):
        self.generated_rooms = {start_room: random.choice(ROOM_CENTER_VARIANTS)}
        self.current_room_pos = start_room
        self.current_map = self.generated_rooms[start_room]

    def set_room(self, room_pos):
        self.current_room_pos = room_pos
        self.current_map = self.generated_rooms[room_pos]

    def ensure_room_exists(self, room_pos, exit_dir):
        if room_pos not in self.generated_rooms:
            self.generated_rooms[room_pos] = generate_room_by_exit(exit_dir)

    def width(self):
        return len(self.current_map[0])

    def height(self):
        return len(self.current_map)

    def get_tile(self, tx, ty):
        if 0 <= ty < self.height() and 0 <= tx < self.width():
            return self.current_map[ty][tx]
        return "0"

    def is_walkable_tile(self, tx, ty):
        return self.get_tile(tx, ty) in ("1", "2", "3", "4", "5")

    def get_exit_direction(self, tx, ty):
        if self.get_tile(tx, ty) != "2":
            return None
        if ty == 0:
            return "up"
        if ty == self.height() - 1:
            return "down"
        if tx == 0:
            return "left"
        if tx == self.width() - 1:
            return "right"
        return None

    def get_next_room_pos(self, exit_dir):
        x, y = self.current_room_pos
        dx, dy = ROOM_DIRS[exit_dir]
        return (x + dx, y + dy)

    def find_spawn_from_entry(self, entry_dir):
        target_side = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }[entry_dir]

        candidates = []
        for y, row in enumerate(self.current_map):
            for x, ch in enumerate(row):
                if ch != "2":
                    continue
                if target_side == "up" and y == 0:
                    candidates.append((x, y))
                elif target_side == "down" and y == self.height() - 1:
                    candidates.append((x, y))
                elif target_side == "left" and x == 0:
                    candidates.append((x, y))
                elif target_side == "right" and x == self.width() - 1:
                    candidates.append((x, y))

        if not candidates:
            return None

        cx = self.width() // 2
        cy = self.height() // 2
        candidates.sort(key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        return candidates[0]


# =========================================================
# Player
# =========================================================
class Player:
    def __init__(self, job_name, tile_x, tile_y):
        data = CLASS_DATA[job_name]
        self.job = job_name
        self.job_label = data["name"]

        self.level = 1
        self.exp = 0
        self.exp_to_next = self.calc_exp_to_next()

        self.intelligence = data["intelligence"]
        self.vitality = data["vitality"]
        self.muscle = data["muscle"]

        self.max_hp = data["max_hp"]
        self.max_mp = data["max_mp"]
        self.hp = float(self.max_hp)
        self.mp = float(self.max_mp)

        self.hp_regen = data["hp_regen"]
        self.mp_regen = data["mp_regen"]

        self.body = [(tile_x, tile_y), (tile_x - 1, tile_y), (tile_x - 2, tile_y)]
        self.desired_length = 3

        self.facing = "right"
        self.next_direction = "right"

        self.base_move_interval = 0.18
        self.boost_move_interval = 0.11
        self.move_timer = 0.0

        self.invincible_until = 0
        self.speed_boost_until = 0

        self.space_invincible_until = 0
        self.stunned_until = 0

        self.attack_cooldown_until = 0
        self.command_buffer = deque()

    def calc_exp_to_next(self):
        return 15 * self.level

    def regen(self, dt):
        self.hp = min(self.max_hp, self.hp + self.hp_regen * dt)
        self.mp = min(self.max_mp, self.mp + self.mp_regen * dt)

    def head(self):
        return self.body[0]

    def can_act(self, now):
        return now >= self.stunned_until

    def get_move_interval(self, now):
        return self.boost_move_interval if now < self.speed_boost_until else self.base_move_interval

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next and self.level < 30:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = self.calc_exp_to_next()
            self.desired_length += 1

            if self.job == "warrior":
                self.muscle += 1
                self.vitality += 3
                self.max_hp += 8
                self.max_mp += 2
            else:
                self.intelligence += 2
                self.vitality += 1
                self.max_hp += 4
                self.max_mp += 8

            self.hp = self.max_hp
            self.mp = self.max_mp

    def take_damage(self, amount, now):
        if now < self.invincible_until:
            return False
        self.hp -= amount
        self.invincible_until = now + 500
        self.speed_boost_until = now + 700
        return True

    def use_space_skill(self, now):
        if self.job != "warrior":
            return
        if now < self.attack_cooldown_until:
            return
        self.space_invincible_until = now + 500
        self.invincible_until = max(self.invincible_until, self.space_invincible_until)
        self.stunned_until = now + 1000
        self.attack_cooldown_until = now + 1800

    def update_command_buffer(self, key_name, now):
        self.command_buffer.append((key_name, now))
        while self.command_buffer and now - self.command_buffer[0][1] > 1000:
            self.command_buffer.popleft()

    def check_fireball_command(self):
        seq = [k for k, _ in self.command_buffer]
        return len(seq) >= 4 and seq[-4:] == ["w", "w", "a", "w"]

    def clear_command(self):
        self.command_buffer.clear()

    def set_next_direction(self, new_dir):
        if new_dir == OPPOSITE[self.facing]:
            return
        self.next_direction = new_dir

    def try_advance(self, map_manager, now):
        if now < self.stunned_until:
            return False

        self.facing = self.next_direction
        dx, dy = MOVE_DIRS[self.facing]
        hx, hy = self.head()
        nx, ny = hx + dx, hy + dy

        if not map_manager.is_walkable_tile(nx, ny):
            return False

        body_to_check = self.body[:-1] if len(self.body) >= self.desired_length else self.body
        if (nx, ny) in body_to_check:
            return False

        self.body.insert(0, (nx, ny))
        while len(self.body) > self.desired_length:
            self.body.pop()
        return True


# =========================================================
# Enemy Projectile
# =========================================================
class EnemyProjectile:
    def __init__(self, start_tile, target_tile, damage):
        self.x = start_tile[0] * TILE_SIZE + TILE_SIZE // 2
        self.y = start_tile[1] * TILE_SIZE + TILE_SIZE // 2
        self.radius = 7
        self.speed = 260
        self.damage = damage
        self.alive = True

        tx = target_tile[0] * TILE_SIZE + TILE_SIZE // 2
        ty = target_tile[1] * TILE_SIZE + TILE_SIZE // 2
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy) or 1

        self.vx = dx / dist * self.speed
        self.vy = dy / dist * self.speed

    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt, player, map_manager, now):
        if not self.alive:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        tx = int(self.x // TILE_SIZE)
        ty = int(self.y // TILE_SIZE)

        if not map_manager.is_walkable_tile(tx, ty):
            self.alive = False
            return

        player_rects = [tile_rect(x, y) for x, y in player.body]
        if any(self.rect().colliderect(r) for r in player_rects):
            player.take_damage(self.damage, now)
            self.alive = False


# =========================================================
# Monster Base
# =========================================================
class BaseMonster:
    def __init__(self, tile_x, tile_y, player_level):
        self.tx = tile_x
        self.ty = tile_y
        self.player_level = player_level
        self.state = "idle"
        self.state_timer = 0.0
        self.warning_tiles = []
        self.attack_cooldown_until = 0

    def rect(self):
        return tile_rect(self.tx, self.ty)

    def update(self, dt, player, map_manager, now, enemy_projectiles):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError


class ChargerMonster(BaseMonster):
    def __init__(self, tile_x, tile_y, player_level):
        super().__init__(tile_x, tile_y, player_level)
        self.damage = 12 + 1.5 * player_level
        self.max_hp = 20 + 3 * player_level
        self.hp = self.max_hp
        self.exp_reward = 3 + 2 * player_level
        self.charge_duration = 3.0
        self.dash_steps = 4
        self.dash_dir = (0, 0)

    def update(self, dt, player, map_manager, now, enemy_projectiles):
        self.state_timer += dt

        if self.state == "idle":
            self.state = "charging"
            self.state_timer = 0.0

            px, py = player.head()
            dx = px - self.tx
            dy = py - self.ty
            if abs(dx) >= abs(dy):
                self.dash_dir = (1 if dx > 0 else -1 if dx < 0 else 0, 0)
            else:
                self.dash_dir = (0, 1 if dy > 0 else -1 if dy < 0 else 0)

            self.warning_tiles = []
            wx, wy = self.tx, self.ty
            for _ in range(self.dash_steps):
                wx += self.dash_dir[0]
                wy += self.dash_dir[1]
                if not map_manager.is_walkable_tile(wx, wy):
                    break
                self.warning_tiles.append((wx, wy))

        elif self.state == "charging":
            if self.state_timer >= self.charge_duration:
                for _ in range(self.dash_steps):
                    nx = self.tx + self.dash_dir[0]
                    ny = self.ty + self.dash_dir[1]
                    if not map_manager.is_walkable_tile(nx, ny):
                        break
                    self.tx, self.ty = nx, ny
                    if (self.tx, self.ty) in player.body:
                        player.take_damage(self.damage, now)

                self.warning_tiles = []
                self.state = "idle"
                self.state_timer = 0.0

    def draw(self, surface):
        rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
        pygame.draw.rect(surface, (200, 80, 80), rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)


class ShooterMonster(BaseMonster):
    def __init__(self, tile_x, tile_y, player_level):
        super().__init__(tile_x, tile_y, player_level)
        self.damage = 7 + 1.5 * player_level
        self.max_hp = 10 + 3 * player_level
        self.hp = self.max_hp
        self.exp_reward = 5 + 2 * player_level
        self.fire_cooldown = 1.8

    def update(self, dt, player, map_manager, now, enemy_projectiles):
        if now < self.attack_cooldown_until:
            return

        px, py = player.head()
        if abs(px - self.tx) <= 1 and abs(py - self.ty) <= 1:
            enemy_projectiles.append(EnemyProjectile((self.tx, self.ty), (px, py), self.damage))
            self.attack_cooldown_until = now + int(self.fire_cooldown * 1000)

    def draw(self, surface):
        rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
        pygame.draw.rect(surface, (80, 120, 220), rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)


class StabberMonster(BaseMonster):
    def __init__(self, tile_x, tile_y, player_level):
        super().__init__(tile_x, tile_y, player_level)
        self.damage = 15 + 1.5 * player_level
        self.max_hp = 35 + 3 * player_level
        self.hp = self.max_hp
        self.exp_reward = 10 + 2 * player_level
        self.move_interval = max(0.28 - min(player_level * 0.003, 0.08), 0.14)
        self.move_timer = 0.0
        self.stab_dir = (0, 0)

    def get_stab_tiles(self):
        x, y = self.tx, self.ty
        dx, dy = self.stab_dir
        return [(x + dx * i, y + dy * i) for i in range(1, 4)]

    def update(self, dt, player, map_manager, now, enemy_projectiles):
        self.state_timer += dt
        px, py = player.head()

        if self.state == "idle":
            if abs(px - self.tx) <= 1 and abs(py - self.ty) <= 1:
                self.state = "windup"
                self.state_timer = 0.0

                dx = px - self.tx
                dy = py - self.ty
                if abs(dx) >= abs(dy):
                    self.stab_dir = (1 if dx > 0 else -1 if dx < 0 else 0, 0)
                else:
                    self.stab_dir = (0, 1 if dy > 0 else -1 if dy < 0 else 0)
            else:
                self.move_timer += dt
                if self.move_timer >= self.move_interval:
                    self.move_timer = 0.0

                    dx = px - self.tx
                    dy = py - self.ty
                    candidates = []

                    if abs(dx) >= abs(dy):
                        if dx > 0:
                            candidates.append((self.tx + 1, self.ty))
                        elif dx < 0:
                            candidates.append((self.tx - 1, self.ty))
                        if dy > 0:
                            candidates.append((self.tx, self.ty + 1))
                        elif dy < 0:
                            candidates.append((self.tx, self.ty - 1))
                    else:
                        if dy > 0:
                            candidates.append((self.tx, self.ty + 1))
                        elif dy < 0:
                            candidates.append((self.tx, self.ty - 1))
                        if dx > 0:
                            candidates.append((self.tx + 1, self.ty))
                        elif dx < 0:
                            candidates.append((self.tx - 1, self.ty))

                    candidates.extend([
                        (self.tx + 1, self.ty),
                        (self.tx - 1, self.ty),
                        (self.tx, self.ty + 1),
                        (self.tx, self.ty - 1),
                    ])

                    for nx, ny in candidates:
                        if not map_manager.is_walkable_tile(nx, ny):
                            continue
                        self.tx, self.ty = nx, ny
                        break

        elif self.state == "windup":
            self.warning_tiles = self.get_stab_tiles()
            if self.state_timer >= 1.0:
                for tx, ty in self.warning_tiles:
                    if (tx, ty) in player.body:
                        player.take_damage(self.damage, now)
                self.warning_tiles = []
                self.state = "idle"
                self.state_timer = 0.0

    def draw(self, surface):
        rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
        pygame.draw.rect(surface, (160, 60, 200), rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)


# =========================================================
# Player Fireball
# =========================================================
class Fireball:
    def __init__(self, start_tile, target_tile, damage):
        self.x = start_tile[0] * TILE_SIZE + TILE_SIZE // 2
        self.y = start_tile[1] * TILE_SIZE + TILE_SIZE // 2
        self.radius = 8
        self.speed = 360
        self.damage = damage
        self.alive = True

        tx = target_tile[0] * TILE_SIZE + TILE_SIZE // 2
        ty = target_tile[1] * TILE_SIZE + TILE_SIZE // 2
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy) or 1

        self.vx = dx / dist * self.speed
        self.vy = dy / dist * self.speed

    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt, monsters, map_manager):
        if not self.alive:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        tx = int(self.x // TILE_SIZE)
        ty = int(self.y // TILE_SIZE)

        if not map_manager.is_walkable_tile(tx, ty):
            self.alive = False
            return

        for monster in monsters:
            if self.rect().colliderect(monster.rect()):
                monster.hp -= self.damage
                self.alive = False
                break


# =========================================================
# 공격 판정
# =========================================================
def get_warrior_attack_tiles(player):
    hx, hy = player.head()
    tiles = []

    if player.facing == "up":
        for y in range(hy - 2, hy):
            for x in range(hx - 1, hx + 2):
                tiles.append((x, y))
    elif player.facing == "down":
        for y in range(hy + 1, hy + 3):
            for x in range(hx - 1, hx + 2):
                tiles.append((x, y))
    elif player.facing == "left":
        for x in range(hx - 2, hx):
            for y in range(hy - 1, hy + 2):
                tiles.append((x, y))
    elif player.facing == "right":
        for x in range(hx + 1, hx + 3):
            for y in range(hy - 1, hy + 2):
                tiles.append((x, y))

    return tiles


# =========================================================
# 랜덤 몬스터 스폰
# =========================================================
def spawn_monsters_for_room(room_map, player, player_level):
    count = random.randint(2, 3)

    monster_classes = [ChargerMonster, ShooterMonster, StabberMonster]
    weights = [40, 35, 25]

    walkable_tiles = []
    for y, row in enumerate(room_map):
        for x, ch in enumerate(row):
            if ch in ("1", "3", "5"):
                walkable_tiles.append((x, y))

    random.shuffle(walkable_tiles)

    selected_positions = []
    monsters = []
    player_head = player.head()

    for tx, ty in walkable_tiles:
        if len(monsters) >= count:
            break

        if manhattan((tx, ty), player_head) < 6:
            continue

        if any(manhattan((tx, ty), pos) < 3 for pos in selected_positions):
            continue

        monster_cls = random.choices(monster_classes, weights=weights, k=1)[0]
        monsters.append(monster_cls(tx, ty, player_level))
        selected_positions.append((tx, ty))

    while len(monsters) < count and walkable_tiles:
        tx, ty = walkable_tiles.pop()
        if any((m.tx, m.ty) == (tx, ty) for m in monsters):
            continue
        monster_cls = random.choices(monster_classes, weights=weights, k=1)[0]
        monsters.append(monster_cls(tx, ty, player_level))

    return monsters


# =========================================================
# 방 전환
# =========================================================
def try_map_transition(player, map_manager):
    hx, hy = player.head()
    exit_dir = map_manager.get_exit_direction(hx, hy)
    if exit_dir is None:
        return None

    next_room_pos = map_manager.get_next_room_pos(exit_dir)
    return {
        "from_room": map_manager.current_room_pos,
        "to_room": next_room_pos,
        "exit_dir": exit_dir,
    }


# =========================================================
# 월드 렌더
# =========================================================
def draw_map(game_map):
    for y, row in enumerate(game_map):
        for x, ch in enumerate(row):
            rect = tile_rect(x, y)

            if ch == "0":
                pygame.draw.rect(screen, DARK_GRAY, rect)
            elif ch == "1":
                if tile_1_img:
                    screen.blit(tile_1_img, rect.topleft)
                else:
                    pygame.draw.rect(screen, (110, 110, 110), rect)
            elif ch == "2":
                pygame.draw.rect(screen, BEIGE, rect)
            elif ch == "3":
                pygame.draw.rect(screen, (70, 140, 70), rect)
            elif ch == "4":
                pygame.draw.rect(screen, (90, 60, 20), rect)
            elif ch == "5":
                pygame.draw.rect(screen, BROWN, rect)

            pygame.draw.rect(screen, BLACK, rect, 1)


def draw_player(player, now):
    visible = True
    if now < player.invincible_until:
        visible = ((now // 80) % 2 == 0)

    if not visible:
        return

    head_color = YELLOW
    body_color = CYAN if player.job == "mage" else GREEN

    for i, (x, y) in enumerate(player.body):
        rect = tile_rect(x, y).inflate(-6, -6)
        color = head_color if i == 0 else body_color
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)


def draw_fireballs(fireballs):
    for fb in fireballs:
        pygame.draw.circle(screen, ORANGE, (int(fb.x), int(fb.y)), fb.radius)
        pygame.draw.circle(screen, RED, (int(fb.x), int(fb.y)), fb.radius, 2)


def draw_enemy_projectiles(enemy_projectiles):
    for ep in enemy_projectiles:
        pygame.draw.circle(screen, (255, 80, 120), (int(ep.x), int(ep.y)), ep.radius)
        pygame.draw.circle(screen, BLACK, (int(ep.x), int(ep.y)), ep.radius, 2)


def draw_attack_tiles(tiles, map_manager):
    for tx, ty in tiles:
        if 0 <= tx < map_manager.width() and 0 <= ty < map_manager.height():
            pygame.draw.rect(screen, WHITE, tile_rect(tx, ty), 3)


def draw_monster_warnings(monsters, map_manager):
    for monster in monsters:
        for tx, ty in getattr(monster, "warning_tiles", []):
            if 0 <= tx < map_manager.width() and 0 <= ty < map_manager.height():
                pygame.draw.rect(screen, RED, tile_rect(tx, ty), 3)


# =========================================================
# UI
# =========================================================
def draw_player_ui(player, now, total_rooms, room_pos):
    panel_x = 15
    panel_y = GAME_HEIGHT + 8
    panel_w = 410
    panel_h = 118

    pygame.draw.rect(screen, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

    hex_center = (panel_x + 55, panel_y + 48)
    draw_hex_frame(screen, hex_center, 34, WHITE, 3)

    char_color = CYAN if player.job == "mage" else GREEN
    pygame.draw.circle(screen, char_color, hex_center, 18)
    pygame.draw.circle(screen, YELLOW, hex_center, 18, 2)

    bar_x = panel_x + 110
    hp_y = panel_y + 10
    mp_y = panel_y + 40
    exp_y = panel_y + 70
    bar_w = 210

    hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
    hp_color = GREEN
    if hp_ratio < 0.3 and (now // 200) % 2 == 0:
        hp_color = RED

    pygame.draw.rect(screen, RED, (bar_x, hp_y, bar_w, 18))
    pygame.draw.rect(screen, hp_color, (bar_x, hp_y, int(bar_w * hp_ratio), 18))

    mp_ratio = player.mp / player.max_mp if player.max_mp > 0 else 0
    pygame.draw.rect(screen, GRAY, (bar_x, mp_y, bar_w, 18))
    pygame.draw.rect(screen, BLUE, (bar_x, mp_y, int(bar_w * mp_ratio), 18))

    exp_ratio = player.exp / player.exp_to_next if player.exp_to_next > 0 else 0
    pygame.draw.rect(screen, GRAY, (bar_x, exp_y, bar_w, 12))
    pygame.draw.rect(screen, YELLOW, (bar_x, exp_y, int(bar_w * exp_ratio), 12))

    text_x = bar_x + bar_w + 12
    screen.blit(small_font.render(f"HP {int(player.hp)}/{player.max_hp}", True, WHITE), (text_x, hp_y - 1))
    screen.blit(small_font.render(f"MP {int(player.mp)}/{player.max_mp}", True, WHITE), (text_x, mp_y - 1))
    screen.blit(small_font.render(f"Lv {player.level}", True, WHITE), (text_x, exp_y - 4))

    info_y = panel_y + 92
    screen.blit(small_font.render(f"직업: {player.job_label}", True, WHITE), (panel_x + 15, info_y))
    screen.blit(small_font.render(f"좌표: {room_pos}", True, WHITE), (panel_x + 120, info_y))
    screen.blit(small_font.render(f"방 수: {total_rooms}", True, WHITE), (panel_x + 240, info_y))


def draw_command_ui(player, now):
    panel_x = 445
    panel_y = GAME_HEIGHT + 8
    panel_w = 320
    panel_h = 118

    pygame.draw.rect(screen, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

    title = font.render("COMMAND", True, WHITE)
    title_rect = title.get_rect(center=(panel_x + panel_w // 2, panel_y + 18))
    screen.blit(title, title_rect)

    seq = [k.upper() for k, _ in player.command_buffer]
    text = " ".join(seq) if seq else "-"
    cmd_surface = font.render(text, True, CYAN)
    cmd_rect = cmd_surface.get_rect(center=(panel_x + panel_w // 2, panel_y + 52))
    screen.blit(cmd_surface, cmd_rect)

    if player.job == "mage":
        if player.check_fireball_command():
            status = small_font.render("Fireball READY", True, YELLOW)
        else:
            status = small_font.render("Input: W W A W", True, GRAY)
    else:
        remain = max(0.0, (player.attack_cooldown_until - now) / 1000.0)
        if remain > 0:
            status = small_font.render(f"Slash CD: {remain:.1f}s", True, GRAY)
        else:
            status = small_font.render("Slash READY", True, GREEN)

    status_rect = status.get_rect(center=(panel_x + panel_w // 2, panel_y + 88))
    screen.blit(status, status_rect)


def draw_minimap_ui(current_room_pos, visited_rooms):
    panel_x = WIDTH - 145
    panel_y = GAME_HEIGHT + 8
    panel_w = 125
    panel_h = 118

    pygame.draw.rect(screen, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

    title = font.render("MAP", True, WHITE)
    title_rect = title.get_rect(center=(panel_x + panel_w // 2, panel_y + 18))
    screen.blit(title, title_rect)

    minimap_size = 10
    gap = 4

    cur_x, cur_y = current_room_pos
    drawn_edges = set()

    center_x = panel_x + panel_w // 2
    center_y = panel_y + 68

    for room_pos in visited_rooms:
        rx, ry = room_pos
        dx1 = rx - cur_x
        dy1 = -(ry - cur_y)

        x1 = center_x + dx1 * (minimap_size + gap)
        y1 = center_y + dy1 * (minimap_size + gap)

        for _, (mx, my) in ROOM_DIRS.items():
            next_room = (rx + mx, ry + my)
            if next_room not in visited_rooms:
                continue

            edge = tuple(sorted([room_pos, next_room]))
            if edge in drawn_edges:
                continue
            drawn_edges.add(edge)

            x2 = center_x + (next_room[0] - cur_x) * (minimap_size + gap)
            y2 = center_y + (-(next_room[1] - cur_y)) * (minimap_size + gap)
            pygame.draw.line(screen, GRAY, (x1, y1), (x2, y2), 2)

    for room_pos in visited_rooms:
        rx, ry = room_pos
        dx = rx - cur_x
        dy = -(ry - cur_y)

        draw_x = center_x + dx * (minimap_size + gap) - minimap_size // 2
        draw_y = center_y + dy * (minimap_size + gap) - minimap_size // 2

        rect = pygame.Rect(draw_x, draw_y, minimap_size, minimap_size)

        if room_pos == current_room_pos:
            pygame.draw.rect(screen, YELLOW, rect, border_radius=2)
            pygame.draw.rect(screen, BLACK, rect, 1, border_radius=2)
        else:
            pygame.draw.rect(screen, WHITE, rect, border_radius=2)
            pygame.draw.rect(screen, BLACK, rect, 1, border_radius=2)


def draw_full_ui(player, now, visited_rooms, map_manager):
    pygame.draw.rect(screen, BLACK, (0, GAME_HEIGHT, WIDTH, UI_HEIGHT))
    draw_player_ui(player, now, len(map_manager.generated_rooms), map_manager.current_room_pos)
    draw_command_ui(player, now)
    draw_minimap_ui(map_manager.current_room_pos, visited_rooms)


# =========================================================
# 메시지
# =========================================================
def draw_message(text, sub=""):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title = big_font.render(text, True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

    if sub:
        t2 = font.render(sub, True, WHITE)
        screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))


# =========================================================
# 직업 선택
# =========================================================
def select_job():
    while True:
        screen.fill(DARK_GRAY)

        title = big_font.render("직업 선택", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        warrior_text = font.render("1 : 전사", True, GREEN)
        mage_text = font.render("2 : 마법사", True, CYAN)

        screen.blit(warrior_text, warrior_text.get_rect(center=(WIDTH // 2, 240)))
        screen.blit(mage_text, mage_text.get_rect(center=(WIDTH // 2, 300)))

        guide1 = small_font.render("전사: 자동 전진 / X 베기 / Space 무적 후 경직", True, WHITE)
        guide2 = small_font.render("마법사: 자동 전진 / 1초 안에 W,W,A,W 후 X", True, WHITE)
        guide3 = small_font.render("방향키로 방향 전환 / 방은 무한 생성", True, WHITE)

        screen.blit(guide1, guide1.get_rect(center=(WIDTH // 2, 390)))
        screen.blit(guide2, guide2.get_rect(center=(WIDTH // 2, 420)))
        screen.blit(guide3, guide3.get_rect(center=(WIDTH // 2, 450)))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return "warrior"
                if e.key == pygame.K_2:
                    return "mage"


# =========================================================
# 메인
# =========================================================
def main():
    job = select_job()

    map_manager = MapManager((0, 0))
    player = Player(job, 15, 9)

    monsters = spawn_monsters_for_room(map_manager.current_map, player, player.level)
    fireballs = []
    enemy_projectiles = []

    visited_rooms = {map_manager.current_room_pos}

    attack_tiles = []
    attack_effect_until = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    player.set_next_direction("up")
                elif e.key == pygame.K_DOWN:
                    player.set_next_direction("down")
                elif e.key == pygame.K_LEFT:
                    player.set_next_direction("left")
                elif e.key == pygame.K_RIGHT:
                    player.set_next_direction("right")

                if player.job == "warrior":
                    if e.key == pygame.K_SPACE:
                        player.use_space_skill(now)

                    if e.key == pygame.K_x and now >= player.attack_cooldown_until and player.can_act(now):
                        dmg = 5 + player.muscle * player.level
                        attack_tiles = get_warrior_attack_tiles(player)
                        attack_effect_until = now + 120
                        player.attack_cooldown_until = now + 350

                        for monster in monsters:
                            if (monster.tx, monster.ty) in attack_tiles:
                                monster.hp -= dmg

                elif player.job == "mage":
                    if e.key == pygame.K_w:
                        player.update_command_buffer("w", now)
                    elif e.key == pygame.K_a:
                        player.update_command_buffer("a", now)
                    elif e.key == pygame.K_s:
                        player.update_command_buffer("s", now)
                    elif e.key == pygame.K_d:
                        player.update_command_buffer("d", now)

                    if e.key == pygame.K_x and player.can_act(now):
                        if player.check_fireball_command() and player.mp >= 10:
                            player.mp -= 10
                            dmg = 10 + player.intelligence * player.level

                            if monsters:
                                target = min(monsters, key=lambda m: manhattan(player.head(), (m.tx, m.ty)))
                                fireballs.append(Fireball(player.head(), (target.tx, target.ty), dmg))
                            else:
                                hx, hy = player.head()
                                dx, dy = MOVE_DIRS[player.facing]
                                fireballs.append(Fireball(player.head(), (hx + dx * 5, hy + dy * 5), dmg))

                            player.clear_command()
                            player.attack_cooldown_until = now + 250

        player.move_timer += dt
        move_interval = player.get_move_interval(now)

        while player.move_timer >= move_interval:
            player.move_timer -= move_interval
            moved = player.try_advance(map_manager, now)

            if moved:
                transition = try_map_transition(player, map_manager)
                if transition:
                    next_room_pos = transition["to_room"]

                    map_manager.ensure_room_exists(next_room_pos, transition["exit_dir"])
                    map_manager.set_room(next_room_pos)
                    visited_rooms.add(map_manager.current_room_pos)

                    spawn_tile = map_manager.find_spawn_from_entry(transition["exit_dir"])
                    if spawn_tile:
                        sx, sy = spawn_tile

                        if transition["exit_dir"] == "up":
                            sy -= 1
                        elif transition["exit_dir"] == "down":
                            sy += 1
                        elif transition["exit_dir"] == "left":
                            sx -= 1
                        elif transition["exit_dir"] == "right":
                            sx += 1

                        player.body = [(sx, sy)]
                        dx, dy = MOVE_DIRS[OPPOSITE[player.facing]]
                        for i in range(1, player.desired_length):
                            player.body.append((sx + dx * i, sy + dy * i))

                    monsters = spawn_monsters_for_room(map_manager.current_map, player, player.level)
                    fireballs.clear()
                    enemy_projectiles.clear()
                    attack_tiles.clear()
                    break

        player.regen(dt)

        for monster in monsters:
            monster.update(dt, player, map_manager, now, enemy_projectiles)

        for fb in fireballs:
            fb.update(dt, monsters, map_manager)
        fireballs = [fb for fb in fireballs if fb.alive]

        for ep in enemy_projectiles:
            ep.update(dt, player, map_manager, now)
        enemy_projectiles = [ep for ep in enemy_projectiles if ep.alive]

        dead = [m for m in monsters if m.hp <= 0]
        for m in dead:
            player.gain_exp(m.exp_reward)
            monsters.remove(m)

        if not monsters:
            monsters = spawn_monsters_for_room(map_manager.current_map, player, player.level)

        if player.hp <= 0:
            while True:
                screen.fill(BLACK)
                draw_message("GAME OVER", "R : 재시작 / Q : 종료")
                pygame.display.flip()

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_r:
                            main()
                            return
                        if e.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()

        screen.fill(BLACK)
        draw_map(map_manager.current_map)

        if now < attack_effect_until:
            draw_attack_tiles(attack_tiles, map_manager)

        draw_monster_warnings(monsters, map_manager)

        for monster in monsters:
            monster.draw(screen)

        draw_enemy_projectiles(enemy_projectiles)
        draw_fireballs(fireballs)
        draw_player(player, now)
        draw_full_ui(player, now, visited_rooms, map_manager)

        pygame.display.flip()


if __name__ == "__main__":
    main()
