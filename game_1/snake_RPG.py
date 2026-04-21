import pygame
import sys
import math
import random
import os
import sys
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMG_DIR = os.path.join(BASE_DIR, "Game_image")
SOUND_DIR = os.path.join(BASE_DIR, "sound_tracks")

print("BASE_DIR =", BASE_DIR)
print("IMG_DIR =", IMG_DIR)
print("SOUND_DIR =", SOUND_DIR)
print("player_head exists =", os.path.exists(os.path.join(IMG_DIR, "player_head.png")))
print("ground exists =", os.path.exists(os.path.join(IMG_DIR, "ground.png")))
print("bgm exists =", os.path.exists(os.path.join(SOUND_DIR, "game_bgm.wav")))


pygame.init()
pygame.mixer.init()

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

# 실제 모니터 해상도
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# 실제 출력용 전체화면
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Snake Worm RPG Prototype - Infinite Rooms")

# 내부 게임용 고정 해상도 Surface
game_surface = pygame.Surface((WIDTH, HEIGHT))

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
# 보스 설정
# =========================================================
BOSS_ROOM_POS = (0, 3)   # 예시: 시작방에서 위로 3칸 간 방
BOSS_MIN_LEVEL = 1
BOSS_HP = 700

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
# 아이템 데이터
# =========================================================
ITEM_KNIFE = 10
ITEM_FROG_TONGUE = 11
ITEM_ARMOR = 12
ITEM_BOMB = 13
ITEM_POISON_HOOD = 14

ITEM_NAMES = {
    ITEM_KNIFE: "식칼",
    ITEM_FROG_TONGUE: "개구리 혀",
    ITEM_ARMOR: "갑주",
    ITEM_BOMB: "폭탄",
    ITEM_POISON_HOOD: "독에 젖은 후드",
}



# =========================================================
# 직업 데이터
# =========================================================
CLASS_DATA = {
    "warrior": {
        "name": "전사",
        "max_hp": 100,
        "max_mp": 100,
        "hp_regen": 0.6,
        "mp_regen": 10,
        "intelligence": 0,
        "vitality": 5,
        "muscle": 5,
    },
    "mage": {
        "name": "마법사",
        "max_hp": 50,
        "max_mp": 100,
        "hp_regen": 0.2,
        "mp_regen": 2.4,
        "intelligence": 6,
        "vitality": 2,
        "muscle": 0,
    },
}

# =========================================================
# 이미지 로드
# =========================================================

def load_portrait(path, size=(80, 80)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"초상화 로드 실패: {path}, {e}")
        return None


PORTRAITS = {
    "warrior": {
        "idle": load_portrait(os.path.join(IMG_DIR, "warrior_idle.png")),
        "sad": load_portrait(os.path.join(IMG_DIR, "warrior_sad.png")),
    },
    "mage": {
       "idle": load_portrait(os.path.join(IMG_DIR, "mage_idle.png")),
       "sad": load_portrait(os.path.join(IMG_DIR, "mage_sad.png")),
    }
}


def load_player_part(path, size=(TILE_SIZE, TILE_SIZE)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"플레이어 파츠 로드 실패: {path}, {e}")
        return None

PLAYER_HEAD_IMG = load_player_part(os.path.join(IMG_DIR, "player_head.png"))
PLAYER_BODY_IMG = load_player_part(os.path.join(IMG_DIR, "player_body.png"))
PLAYER_TAIL_IMG = load_player_part(os.path.join(IMG_DIR, "player_tail.png"))

def load_tile(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"타일 없음: {path}")

    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

TILES = {
    "ground": load_tile(os.path.join(IMG_DIR, "ground.png")),
    "tile": load_tile(os.path.join(IMG_DIR, "tile.png")),
    "edge_tile": load_tile(os.path.join(IMG_DIR, "edge_tile.png")),
    "inner_corner_tile": load_tile(os.path.join(IMG_DIR, "inner_corner_tile.png")),
}


def load_sprite(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size is not None:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"스프라이트 로드 실패: {path}, {e}")
        return None


def load_animation_frames(paths, size=None):
    frames = []
    for path in paths:
        img = load_sprite(path, size)
        if img:
            frames.append(img)
    return frames
## Monster 3

MONSTER_1_IDLE_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_1_idle.png"),
], size=(TILE_SIZE, TILE_SIZE))

MONSTER_1_ROLL_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_1_idle.png"),
    os.path.join(IMG_DIR, "Monster_1_rolling_1.png"),
    os.path.join(IMG_DIR, "Monster_1_rolling_2.png"),
], size=(TILE_SIZE, TILE_SIZE))
## Monster 2
MONSTER_2_FRONT_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_2_front.png"),
], size=(TILE_SIZE, TILE_SIZE))

MONSTER_2_BACK_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_2_back.png"),
], size=(TILE_SIZE, TILE_SIZE))
## Monster 3
MONSTER_3_IDLE_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_3.png"),
], size=(TILE_SIZE, TILE_SIZE))

MONSTER_3_EFFECT_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_3_effect_1.png"),
    os.path.join(IMG_DIR, "Monster_3_effect_2.png"),
    os.path.join(IMG_DIR, "Monster_3_effect_3.png"),
    os.path.join(IMG_DIR, "Monster_3_effect_4.png"),
], size=(TILE_SIZE, TILE_SIZE))

MONSTER_4_IDLE_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "monster_4_1.png"),
    os.path.join(IMG_DIR, "monster_4_2.png"),
    os.path.join(IMG_DIR, "monster_4_3.png"),
    os.path.join(IMG_DIR, "monster_4_4.png"),
], size=(TILE_SIZE, TILE_SIZE))

MONSTER_5_IDLE_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Monster_5_1.png"),
    os.path.join(IMG_DIR, "Monster_5_2.png"),
    os.path.join(IMG_DIR, "Monster_5_3.png"),
], size=(TILE_SIZE, TILE_SIZE))

MONSTER_4_EFFECT_IMG = load_sprite(
    os.path.join(IMG_DIR, "Explosion SpriteSheet.png"),
    size=(TILE_SIZE * 3, TILE_SIZE * 3)
)

MONSTER_5_EFFECT_IMG = load_sprite(
    os.path.join(IMG_DIR, "poison.png"),
    size=(TILE_SIZE * 5, TILE_SIZE * 5)
)

##Player effect

PLAYER_SLASH_FRAMES = load_animation_frames([
    os.path.join(IMG_DIR, "Player_effect_1.png"),
    os.path.join(IMG_DIR, "Player_effect_2.png"),
    os.path.join(IMG_DIR, "Player_effect_3.png"),
    os.path.join(IMG_DIR, "Player_effect_4.png"),
    os.path.join(IMG_DIR, "Player_effect_5.png"),
    os.path.join(IMG_DIR, "Player_effect_6.png"),
    os.path.join(IMG_DIR, "Player_effect_7.png"),
    os.path.join(IMG_DIR, "Player_effect_8.png"),
], size=(TILE_SIZE * 4, TILE_SIZE * 4))


BOSS_HAND_IDLE_IMG = load_sprite(
    os.path.join(IMG_DIR, "THE_HAND_IDLE.png"),
    size=(TILE_SIZE * 4, TILE_SIZE * 3)
)

BOSS_HAND_BANG_IMG = load_sprite(
    os.path.join(IMG_DIR, "THE_HAND_BANG.png"),
    size=(TILE_SIZE * 4, TILE_SIZE * 3)
)

BOSS_HAND_ROCK_IMG = load_sprite(
    os.path.join(IMG_DIR, "THE_HAND_ROCK.png"),
    size=(TILE_SIZE * 4, TILE_SIZE * 3)
)
# =========================================================
# 사운드 로드
# =========================================================

def load_sound(path, volume=1.0):
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(volume)
        return s
    except Exception as e:
        print(f"사운드 로드 실패: {path}, {e}")
        return None

SOUNDS = {
    "game_bgm": os.path.join(SOUND_DIR, "game_bgm.wav"),
    "boss_battle": os.path.join(SOUND_DIR, "boss_battle.wav"),
    "player_attack": os.path.join(SOUND_DIR, "player_attack.wav"),
    "hit": os.path.join(SOUND_DIR, "hit.wav"),
    "levelup": os.path.join(SOUND_DIR, "levelup.wav"),
    "reload": os.path.join(SOUND_DIR, "reload_sound.wav"),
    "boss_spawn": os.path.join(SOUND_DIR, "boss.wav"),
    "boss_rock": os.path.join(SOUND_DIR, "boss_rock.wav"),
    "boss_boom": os.path.join(SOUND_DIR, "boss_boom.wav"),
    "boss_dead": os.path.join(SOUND_DIR, "boss_dead.wav"),
}

SFX = {
    "player_attack": load_sound(SOUNDS["player_attack"], 0.5),
    "hit": load_sound(SOUNDS["hit"], 0.5),
    "levelup": load_sound(SOUNDS["levelup"], 0.6),
    "reload": load_sound(SOUNDS["reload"], 0.4),
    "boss_spawn": load_sound(SOUNDS["boss_spawn"], 0.7),
    "boss_rock": load_sound(SOUNDS["boss_rock"], 0.7),
    "boss_boom": load_sound(SOUNDS["boss_boom"], 0.3),
    "boss_dead": load_sound(SOUNDS["boss_dead"], 0.8),
}
# =========================================================
# 방 템플릿
# =========================================================
ROOM_CENTER = [
    "000000000000022222000000000000",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "000000000000011111000000000000",
    "000000000000022222000000000000",
]

ROOM_X = [
    "000000000000000000000000000000",
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
    "000000000000000000000000000000",
]
ROOM_X_2 = [
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
]

ROOM_X_3 = [
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "211111111111111111111111111112",
    "211111111111000000111111111112",
    "211111111111000000111111111112",
    "211111111111000000111111111112",
    "211111111111000000111111111112",
    "211111111111111111111111111112",
    "211111111111111111111111111112",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
]

ROOM_X_4 = [
    "000000000000000000000000000000",
    "000000000000000000000000000000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111100111111001111110000",
    "000011111100111111111111110000",
    "211111111111111111111111111112",
    "211111111111111111110000111112",
    "211111000011111111110000111112",
    "211111111111111111111111111112",
    "211111111111000011111111111112",
    "211111111111111111111111111112",
    "211111000011111111110000111112",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000000000000000000000000000000",
    "000000000000000000000000000000",
]

ROOM_Y = [
    "000000000000222222200000000000",
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
    "000000000000222222200000000000",
]
ROOM_Y_2 = [
    "000000000000222222200000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000111111100000000000",
    "000000000000222222200000000000",
]

ROOM_Y_3 = [
    "000000000000222222200000000000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "011111111111000000111111111110",
    "011111111111000000111111111110",
    "011111111111000000111111111110",
    "011111111111000000111111111110",
    "011111111111000000111111111110",
    "011111111111000000111111111110",
    "011111111111111111111111111110",
    "011111111111111111111111111110",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000000000000222222200000000000",
]

ROOM_Y_4 = [
    "000000000000222222200000000000",
    "000011111100111111001111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000011110000111111110001110000",
    "011111110000111111111111111110",
    "011111111111111111111111111110",
    "011111111111111111110011111110",
    "011111111100001111111111111110",
    "011111111111111111111111111110",
    "011111111111111111110000111110",
    "011111000011111111110000111110",
    "011111111111111111111111111110",
    "000011111111001111111111110000",
    "000011111111001111111111110000",
    "000011111111111111111111110000",
    "000011111111111111111111110000",
    "000000000000222222200000000000",
]

ROOM_X_VARIANTS = [ROOM_X, ROOM_X_2, ROOM_X_3, ROOM_X_4]
ROOM_Y_VARIANTS = [ROOM_Y, ROOM_Y_2, ROOM_Y_3, ROOM_Y_4]
ROOM_CENTER_VARIANTS = [ROOM_CENTER]

# =========================================================
# 폭탄
# =========================================================
def trigger_explosion(center_x, center_y, monsters, boss, damage, radius=1):
    affected_tiles = []

    for y in range(center_y - radius, center_y + radius + 1):
        for x in range(center_x - radius, center_x + radius + 1):
            affected_tiles.append((x, y))

    for monster in monsters:
        if (monster.tx, monster.ty) in affected_tiles:
            monster.hp -= damage

    if boss is not None and boss.alive:
        boss_rect = pygame.Rect(0, 0, TILE_SIZE * 4, TILE_SIZE * 3)
        boss_rect.center = (int(boss.x), int(boss.y))

        for tx, ty in affected_tiles:
            if boss_rect.colliderect(tile_rect(tx, ty)):
                boss.take_damage(damage)
                break
# =========================================================
# 유틸
# =========================================================
def tile_rect(tx, ty):
    return pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)

def play_sfx(name):
    s = SFX.get(name)
    if s:
        s.play()

def play_bgm(path, volume=0.5, loop=True):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
    except Exception as e:
        print(f"BGM 재생 실패: {path}, {e}")
        
def safe_get(map_manager, x, y):
    if x < 0 or y < 0 or x >= map_manager.width() or y >= map_manager.height():
        return "0"
    return map_manager.get_tile(x, y)


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
    

def get_anim_frame(frames, now, frame_duration=120):
    if not frames:
        return None
    idx = (now // frame_duration) % len(frames)
    return frames[idx]

def rotate_by_direction(sprite, direction):
    if sprite is None:
        return None

    if direction == "up":
        return sprite
    elif direction == "right":
        return pygame.transform.rotate(sprite, -90)
    elif direction == "down":
        return pygame.transform.rotate(sprite, 180)
    elif direction == "left":
        return pygame.transform.rotate(sprite, 90)

    return sprite

def get_direction_to_player(monster_x, monster_y, player_x, player_y):
    dx = player_x - monster_x
    dy = player_y - monster_y

    if abs(dx) >= abs(dy):
        if dx > 0:
            return "right"
        elif dx < 0:
            return "left"
    else:
        if dy > 0:
            return "down"
        elif dy < 0:
            return "up"

    return "down"


def body_in_radius(player, center_tx, center_ty, radius):
    for bx, by in player.body:
        if max(abs(bx - center_tx), abs(by - center_ty)) <= radius:
            return True
    return False

def get_portrait_state(player, now):
     if now < player.invincible_until:
         return "sad"
     return "idle"


def get_scaled_size(window_w, window_h, base_w, base_h):
    scale = min(window_w / base_w, window_h / base_h)
    scaled_w = int(base_w * scale)
    scaled_h = int(base_h * scale)
    return scaled_w, scaled_h


def is_player_hit_flash(player, now):
    return now < player.hit_flash_until


def get_screen_shake_offset(player, now):
    if player is None or now >= player.shake_until:
        return 0, 0

    strength = player.shake_strength
    return random.randint(-strength, strength), random.randint(-strength, strength)

def get_boss_hand_sprite(boss):
    if boss is None:
        return None

    if boss.state in ("bang_aim", "bang_fire"):
        return BOSS_HAND_BANG_IMG

    if boss.state in ("fist", "fist_hit"):
        return BOSS_HAND_ROCK_IMG

    return BOSS_HAND_IDLE_IMG

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
        
        self.collision_damage_cooldown_until = 0

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

        self.hit_flash_until = 0
        self.shake_until = 0
        self.shake_strength = 0

        self.items = []
        self.max_items = 2
        self.active_combo = None
        self.combo_effects = {}
        self.refresh_combo()

    def add_item(self, item_id):
        if len(self.items) >= self.max_items:
            return False

        self.items.append(item_id)
        self.refresh_combo()
        return True

    def get_item_combo(self):
        if len(self.items) != 2:
            return None

        a, b = sorted(self.items)

        if self.job == "warrior":
            if (a, b) == (10, 10):
                return "warrior_double_knife"
            elif (a, b) == (10, 11):
                return "warrior_knife_frog"
            elif (a, b) == (10, 13):
                return "warrior_knife_bomb"
            elif (a, b) == (12, 13):
                return "warrior_armor_bomb"

        elif self.job == "mage":
            if (a, b) == (14, 14):
                return "mage_double_poison"
            elif (a, b) == (13, 13):
                return "mage_double_bomb"
            elif (a, b) == (12, 14):
                return "mage_armor_poison"
            elif (a, b) == (13, 14):
                return "mage_bomb_poison"

        return None

    def refresh_combo(self):
        self.active_combo = self.get_item_combo()

        self.combo_effects = {
            "attack_width_bonus": 0,
            "attack_height_bonus": 0,
            "cooldown_mult": 1.0,
            "bomb_on_hit": False,
            "bomb_on_damaged": False,
            "poison_on_hit": False,
            "splash_on_hit": False,
            "spell_explosion": False,
            "spell_heal": False,
            "bonus_muscle": 0,
        }

        if self.active_combo == "warrior_double_knife":
            self.combo_effects["attack_width_bonus"] = 3
            self.combo_effects["attack_height_bonus"] = 1
            self.combo_effects["bonus_muscle"] = 2

        elif self.active_combo == "warrior_knife_frog":
            self.combo_effects["attack_width_bonus"] = 3
            self.combo_effects["attack_height_bonus"] = 1
            self.combo_effects["cooldown_mult"] = 0.7

        elif self.active_combo == "warrior_knife_bomb":
            self.combo_effects["bomb_on_hit"] = True

        elif self.active_combo == "warrior_armor_bomb":
            self.combo_effects["bomb_on_damaged"] = True

        elif self.active_combo == "mage_double_poison":
            self.combo_effects["poison_on_hit"] = True
            self.combo_effects["splash_on_hit"] = True

        elif self.active_combo == "mage_double_bomb":
            self.combo_effects["spell_explosion"] = True

        elif self.active_combo == "mage_armor_poison":
            self.combo_effects["spell_heal"] = True

        elif self.active_combo == "mage_bomb_poison":
            self.combo_effects["splash_on_hit"] = True

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
            play_sfx("levelup")
            self.exp_to_next = self.calc_exp_to_next()
            self.desired_length += 1

            if self.job == "warrior":
                self.muscle += 1
                self.vitality += 3
                self.max_hp += 8
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
        play_sfx("hit")
        self.invincible_until = now + 500
        self.speed_boost_until = now + 700

        self.hit_flash_until = now + 180
        self.shake_until = now + 220
        self.shake_strength = 10

        return True
    
    def take_collision_damage(self, now, amount=5):
        if now < self.collision_damage_cooldown_until:
            return False

        hit = self.take_damage(amount, now)
        if hit:
            self.collision_damage_cooldown_until = now + 400
        return hit

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
            self.take_collision_damage(now, amount=5)
            return False

        body_to_check = self.body[:-1] if len(self.body) >= self.desired_length else self.body
        if (nx, ny) in body_to_check:
            self.take_collision_damage(now, amount=7)
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

    def update(self, dt, player, map_manager, now, monsters, boss):
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
            hit = player.take_damage(self.damage, now)

            if hit and player.combo_effects.get("bomb_on_damaged"):
                hx, hy = player.head()
                trigger_explosion(hx, hy, monsters, boss, self.damage)

            self.alive = False


# =========================================================
# Monster Base
# =========================================================
class BossHand:
    def __init__(self, map_manager):

        self.map_manager = map_manager

        self.x = self.map_manager.width() * TILE_SIZE // 2
        self.y = TILE_SIZE * 2

        self.anchor_x = self.x

        self.max_hp = BOSS_HP
        self.hp = self.max_hp

        self.move_dir = 1
        self.move_speed = 80
        self.move_range = 160

        self.state = "groggy"   # groggy / attack
        self.attack_type = None # x_sweep / y_sweep
        self.state_timer = 0.0

        self.warning_tiles = []
        self.attack_tiles = []

        self.cooldown = random.uniform(2.0, 5.0)
        self.wave_index = 0
        self.wave_timer = 0.0
        self.wave_interval = 0.15

        self.target_tile = None
        self.fist_damage = 15
        self.fist_delay = 0.9

        self.bang_target = None
        self.bang_damage = 25
        self.bang_aim_time = 3.0
        self.bang_shots_total = 3
        self.bang_shots_done = 0
        self.bang_shot_interval = 0.35
        self.bang_shot_timer = 0.0

        self.alive = True
    def choose_next_attack(self, player):
        self.attack_type = random.choice(["x_sweep", "y_sweep", "fist","bang"])
        self.warning_tiles = []
        self.attack_tiles = []
        self.state_timer = 0.0

        if self.attack_type == "bang":
            self.state = "bang_aim"
            self.bang_target = player.head()
            self.warning_tiles = self.get_3x3_tiles(self.bang_target)
            self.attack_tiles = []
            self.bang_shots_done = 0
            self.bang_shot_timer = 0.0

        elif self.attack_type in ("x_sweep", "y_sweep"):
            self.state = "attack"
            self.wave_index = 0
            self.wave_timer = 0.0
            self.target_tile = None

        elif self.attack_type == "fist":
            self.state = "fist"
            self.target_tile = player.head()
            self.warning_tiles = [self.target_tile]
            self.attack_tiles = []

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            play_sfx("boss_dead")
            
    def build_wave_tiles(self):
        tiles = []

        if self.attack_type == "y_sweep":
            # 한 열씩 아래로 훑기
            x = self.wave_index
            for y in range(self.map_manager.height()):
                if self.map_manager.is_walkable_tile(x , y):
                    tiles.append(( x , y ))

        elif self.attack_type == "x_sweep":
            # 한 행씩 오른쪽으로 훑기
            y = self.wave_index
            for x in range(self.map_manager.width()):
                if self.map_manager.is_walkable_tile(x, y ):
                    tiles.append(( x, y ))

        return tiles

    def get_3x3_tiles(self, center_tile):
        if center_tile is None:
            return []

        cx, cy = center_tile
        tiles = []

        for y in range(cy - 1, cy + 2):
            for x in range(cx - 1, cx + 2):
                if 0 <= x < self.map_manager.width() and 0 <= y < self.map_manager.height():
                    if self.map_manager.is_walkable_tile(x, y):
                        tiles.append((x, y))

        return tiles


    def update(self, dt, player, now, monsters, boss):
        if not self.alive:
            return

        self.state_timer += dt

        if self.state in ("groggy", "bang_aim"):
            self.x += self.move_dir * self.move_speed * dt

            if self.x > self.anchor_x + self.move_range:
                self.x = self.anchor_x + self.move_range
                self.move_dir = -1
            elif self.x < self.anchor_x - self.move_range:
                self.x = self.anchor_x - self.move_range
                self.move_dir = 1

        if self.state == "groggy":
            if self.state_timer >= self.cooldown:
                self.state_timer = 0.0
                self.choose_next_attack(player)

        elif self.state == "attack":
            self.wave_timer += dt
            self.warning_tiles = self.build_wave_tiles()

            if self.wave_timer >= self.wave_interval:
                self.wave_timer = 0.0
                self.attack_tiles = list(self.warning_tiles)

                if player.head() in self.attack_tiles:
                    hit = player.take_damage(10, now)
                    if hit and player.combo_effects.get("bomb_on_damaged"):
                        hx, hy = player.head()
                        trigger_explosion(hx, hy, monsters, boss, 10)

                self.wave_index += 1

                if self.attack_type == "y_sweep" and self.wave_index >= self.map_manager.width():
                    self.finish_attack()
                elif self.attack_type == "x_sweep" and self.wave_index >= self.map_manager.height():
                    self.finish_attack()

        elif self.state == "fist":
            self.warning_tiles = [self.target_tile] if self.target_tile else []

            if self.state_timer >= self.fist_delay:
                play_sfx("boss_rock")
                self.warning_tiles = []
                self.attack_tiles = [self.target_tile] if self.target_tile else []

                if self.target_tile is not None and player.head() == self.target_tile:
                    hit = player.take_damage(self.fist_damage, now)
                    if hit and player.combo_effects.get("bomb_on_damaged"):
                        hx, hy = player.head()
                        trigger_explosion(hx, hy, monsters, boss, self.fist_damage)

                self.state = "fist_hit"
                self.state_timer = 0.0

        elif self.state == "fist_hit":
            if self.state_timer >= 0.2:
                self.finish_attack()

        elif self.state == "bang_aim":
            self.warning_tiles = self.get_3x3_tiles(self.bang_target)

            if self.state_timer >= self.bang_aim_time:
                self.state = "bang_fire"
                self.state_timer = 0.0
                self.bang_shot_timer = 0.0
                self.attack_tiles = []

        elif self.state == "bang_fire":
            self.warning_tiles = []
            self.bang_shot_timer += dt

            if self.bang_shot_timer >= self.bang_shot_interval:
                self.bang_shot_timer = 0.0
                play_sfx("boss_boom")
                self.attack_tiles = self.get_3x3_tiles(self.bang_target)

                if player.head() in self.attack_tiles:
                    hit = player.take_damage(self.bang_damage, now)
                    if hit and player.combo_effects.get("bomb_on_damaged"):
                        hx, hy = player.head()
                        trigger_explosion(hx, hy, monsters, boss, self.bang_damage)

                self.bang_shots_done += 1

                if self.bang_shots_done >= self.bang_shots_total:
                    self.finish_attack()
                

    def finish_attack(self):
        self.state = "groggy"
        self.attack_type = None
        self.state_timer = 0.0
        self.cooldown = random.uniform(2.0, 5.0)
        self.wave_index = 0
        self.wave_timer = 0.0
        self.warning_tiles = []
        self.attack_tiles = []
        self.target_tile = None

        self.bang_target = None
        self.bang_shots_done = 0
        self.bang_shot_timer = 0.0

    def draw(self, surface):
        if not self.alive:
            return

        sprite = get_boss_hand_sprite(self)

        if sprite:
            rect = sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(sprite, rect.topleft)

            label = small_font.render(f"BOSS: {self.attack_type or 'groggy'}", True, WHITE)
            surface.blit(label, (rect.x, rect.y - 22))
        else:
            boss_rect = pygame.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 2)
            boss_rect.center = (int(self.x), int(self.y))

            pygame.draw.rect(surface, (180, 120, 120), boss_rect, border_radius=12)
            pygame.draw.rect(surface, BLACK, boss_rect, 3, border_radius=12)

            label = small_font.render(f"BOSS: {self.attack_type or 'groggy'}", True, WHITE)
            surface.blit(label, (boss_rect.x, boss_rect.y - 22))

class BaseMonster:
    def __init__(self, tile_x, tile_y, player_level):
        self.tx = tile_x
        self.ty = tile_y
        self.player_level = player_level
        self.state = "idle"
        self.state_timer = 0.0
        self.warning_tiles = []
        self.attack_cooldown_until = 0
        self.facing = "down"

    def rect(self):
        return tile_rect(self.tx, self.ty)

    def update(self, dt, player, map_manager, now, enemy_projectiles, monsters, boss):
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
        self.charge_duration = 2.0
        self.dash_steps = 8
        self.dash_dir = (0, 0)

    def update(self, dt, player, map_manager, now, enemy_projectiles, monsters, boss):
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

            if abs(dx) >= abs(dy):
                if dx > 0:
                    self.facing = "right"
                elif dx < 0:
                    self.facing = "left"
            else:
                if dy > 0:
                    self.facing = "down"
                elif dy < 0:
                    self.facing = "up"

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
                        hit = player.take_damage(self.damage, now)

                        if hit and player.combo_effects.get("bomb_on_damaged"):
                            hx, hy = player.head()
                            trigger_explosion(hx, hy, monsters, boss, self.damage)

                self.warning_tiles = []
                self.state = "idle"
                self.state_timer = 0.0

    def draw(self, surface):
        now = pygame.time.get_ticks()

        if self.state == "charging":
            sprite = get_anim_frame(MONSTER_1_ROLL_FRAMES, now, 100)
        else:
            sprite = get_anim_frame(MONSTER_1_IDLE_FRAMES, now, 180)

        sprite = rotate_by_direction(sprite, self.facing)

        if sprite:
            rect = sprite.get_rect(center=tile_rect(self.tx, self.ty).center)
            surface.blit(sprite, rect.topleft)
        else:
            rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
            pygame.draw.rect(surface, (200, 80, 80), rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

class ShooterMonster(BaseMonster):
    def __init__(self, tile_x, tile_y, player_level):
        super().__init__(tile_x, tile_y, player_level)
        self.damage = 7 + 1.5 * player_level
        self.max_hp = 15 + 3 * player_level
        self.hp = self.max_hp
        self.exp_reward = 5 + 2 * player_level
        self.fire_cooldown = 1.8

    def update(self, dt, player, map_manager, now, enemy_projectiles, monsters, boss):
        if now < self.attack_cooldown_until:
            return

        px, py = player.head()
        dx = px - self.tx
        dy = py - self.ty

        if abs(dx) >= abs(dy):
            if dx > 0:
                self.facing = "right"
            elif dx < 0:
                self.facing = "left"
        else:
            if dy > 0:
                self.facing = "down"
            elif dy < 0:
                self.facing = "up"

        if abs(px - self.tx) <= 5 and abs(py - self.ty) <= 5:
            enemy_projectiles.append(EnemyProjectile((self.tx, self.ty), (px, py), self.damage))
            self.attack_cooldown_until = now + int(self.fire_cooldown * 1000)
            
    def draw(self, surface):
        now = pygame.time.get_ticks()

        if self.facing == "up":
            sprite = get_anim_frame(MONSTER_2_BACK_FRAMES, now, 200)
        else:
            sprite = get_anim_frame(MONSTER_2_FRONT_FRAMES, now, 200)

        # 좌우는 front 이미지를 좌우 반전해서 사용
        if sprite and self.facing == "left":
            sprite = pygame.transform.flip(sprite, True, False)

        if sprite:
            rect = sprite.get_rect(center=tile_rect(self.tx, self.ty).center)
            surface.blit(sprite, rect.topleft)
        else:
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

    def update(self, dt, player, map_manager, now, enemy_projectiles, monsters, boss):
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
                        hit = player.take_damage(self.damage, now)

                        if hit and player.combo_effects.get("bomb_on_damaged"):
                            hx, hy = player.head()
                            trigger_explosion(hx, hy, monsters, boss, self.damage)

                self.warning_tiles = []
                self.state = "idle"
                self.state_timer = 0.0

    def draw(self, surface):
        now = pygame.time.get_ticks()

        sprite = get_anim_frame(MONSTER_3_IDLE_FRAMES, now, 200)

        if sprite:
            rect = sprite.get_rect(center=tile_rect(self.tx, self.ty).center)
            surface.blit(sprite, rect.topleft)
        else:
            rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
            pygame.draw.rect(surface, (160, 60, 200), rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

        if self.state == "windup":
            effect = get_anim_frame(MONSTER_3_EFFECT_FRAMES, now, 80)
            if effect:
                effect_rect = effect.get_rect(center=tile_rect(self.tx, self.ty).center)
                surface.blit(effect, effect_rect.topleft)

class ExplosionMonster(BaseMonster):
    def __init__(self, tile_x, tile_y, player_level):
        super().__init__(tile_x, tile_y, player_level)
        self.damage = 12 + player_level
        self.max_hp = 28 + 4 * player_level
        self.hp = self.max_hp
        self.exp_reward = 12 + 2 * player_level

        self.attack_radius = 3
        self.move_interval = 0.22
        self.move_timer = 0.0

        self.explode_delay = 2.0
        self.explode_timer = 0.0
        self.is_arming = False
        self.effect_until = 0

    def move_toward_player(self, player, map_manager):
        px, py = player.head()
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

        for nx, ny in candidates:
            if map_manager.is_walkable_tile(nx, ny):
                self.tx, self.ty = nx, ny
                return

    def update(self, dt, player, map_manager, now, enemy_projectiles, monsters, boss):
        px, py = player.head()

        # 가까워지면 폭발 준비
        near_player = body_in_radius(player, self.tx, self.ty, 2)

        if not self.is_arming:
            self.move_timer += dt
            if self.move_timer >= self.move_interval:
                self.move_timer = 0.0
                self.move_toward_player(player, map_manager)

            if near_player:
                self.is_arming = True
                self.explode_timer = 0.0

        else:
            self.explode_timer += dt
            self.effect_until = now + 80

            if self.explode_timer >= self.explode_delay:
                hit = body_in_radius(player, self.tx, self.ty, self.attack_radius)

                if hit:
                    got_hit = player.take_damage(self.damage, now)
                    if got_hit and player.combo_effects.get("bomb_on_damaged"):
                        hx, hy = player.head()
                        trigger_explosion(hx, hy, monsters, boss, self.damage)

                # 자폭
                self.hp = 0

    def draw(self, surface):
        now = pygame.time.get_ticks()

        sprite = get_anim_frame(MONSTER_4_IDLE_FRAMES, now, 120)

        if sprite:
            # 폭발 준비 중이면 빨갛게 변함
            if self.is_arming:
                progress = min(1.0, self.explode_timer / self.explode_delay)
                tinted = sprite.copy()
                red_strength = int(180 * progress)
                tinted.fill((red_strength, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                sprite = tinted

            rect = sprite.get_rect(center=tile_rect(self.tx, self.ty).center)
            surface.blit(sprite, rect.topleft)
        else:
            rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
            base_color = (255, 140, 80)

            if self.is_arming:
                progress = min(1.0, self.explode_timer / self.explode_delay)
                base_color = (
                    min(255, 255),
                    max(0, int(140 * (1.0 - progress))),
                    max(0, int(80 * (1.0 - progress))),
                )

            pygame.draw.rect(surface, base_color, rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

        if self.is_arming and now < self.effect_until:
            cx, cy = tile_rect(self.tx, self.ty).center
            if MONSTER_4_EFFECT_IMG:
                effect_rect = MONSTER_4_EFFECT_IMG.get_rect(center=(cx, cy))
                surface.blit(MONSTER_4_EFFECT_IMG, effect_rect.topleft)

class PoisonMonster(BaseMonster):
    def __init__(self, tile_x, tile_y, player_level):
        super().__init__(tile_x, tile_y, player_level)
        self.damage_per_tick = 1
        self.max_hp = 24 + 3 * player_level
        self.hp = self.max_hp
        self.exp_reward = 11 + 2 * player_level

        self.poison_radius = 2
        self.tick_interval = 1.0
        self.tick_timer = 0.0
        self.effect_until = 0
        self.death_poison_spawned = False

    def update(self, dt, player, map_manager, now, enemy_projectiles, monsters, boss):
        self.tick_timer += dt

        inside = body_in_radius(player, self.tx, self.ty, self.poison_radius)
        if inside:
            self.effect_until = now + 120

        if inside and self.tick_timer >= self.tick_interval:
            self.tick_timer = 0.0

            hit = player.take_damage(self.damage_per_tick, now)
            if hit and player.combo_effects.get("bomb_on_damaged"):
                hx, hy = player.head()
                trigger_explosion(hx, hy, monsters, boss, self.damage_per_tick)

    def draw(self, surface):
        now = pygame.time.get_ticks()

        sprite = get_anim_frame(MONSTER_5_IDLE_FRAMES, now, 150)

        if sprite:
            rect = sprite.get_rect(center=tile_rect(self.tx, self.ty).center)
            surface.blit(sprite, rect.topleft)
        else:
            rect = tile_rect(self.tx, self.ty).inflate(-8, -8)
            pygame.draw.rect(surface, (110, 220, 110), rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

        if now < self.effect_until:
            cx, cy = tile_rect(self.tx, self.ty).center
            if MONSTER_5_EFFECT_IMG:
                effect_rect = MONSTER_5_EFFECT_IMG.get_rect(center=(cx, cy))
                surface.blit(MONSTER_5_EFFECT_IMG, effect_rect.topleft)
                

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
                play_sfx("hit")
                monster.hp -= self.damage
                self.alive = False
                break

# =========================================================
# poison
# ==============================================
class PoisonCloud:
    def __init__(self, tx, ty, radius=2, duration=4.0, tick_damage=1, tick_interval=1.0):
        self.tx = tx
        self.ty = ty
        self.radius = radius
        self.duration = duration
        self.tick_damage = tick_damage
        self.tick_interval = tick_interval

        self.timer = 0.0
        self.tick_timer = 0.0
        self.alive = True

    def update(self, dt, player, now, monsters, boss):
        if not self.alive:
            return

        self.timer += dt
        self.tick_timer += dt

        if self.timer >= self.duration:
            self.alive = False
            return

        if self.tick_timer >= self.tick_interval:
            self.tick_timer = 0.0

            if body_in_radius(player, self.tx, self.ty, self.radius):
                hit = player.take_damage(self.tick_damage, now)
                if hit and player.combo_effects.get("bomb_on_damaged"):
                    hx, hy = player.head()
                    trigger_explosion(hx, hy, monsters, boss, self.tick_damage)

    def draw(self, surface):
        cx, cy = tile_rect(self.tx, self.ty).center

        if MONSTER_5_EFFECT_IMG:
            rect = MONSTER_5_EFFECT_IMG.get_rect(center=(cx, cy))
            surface.blit(MONSTER_5_EFFECT_IMG, rect.topleft)
        else:
            pygame.draw.circle(
                surface,
                (100, 220, 100),
                (cx, cy),
                self.radius * TILE_SIZE,
                2
            )
# =========================================================
# 공격 판정
# =========================================================
def get_warrior_attack_tiles(player):
    hx, hy = player.head()
    tiles = []

    reach = 2
    half_width = 1

    if player.combo_effects.get("attack_width_bonus", 0) > 0:
        reach = 5
        half_width = 1

    if player.facing == "up":
        for y in range(hy - reach, hy):
            for x in range(hx - half_width, hx + half_width + 1):
                tiles.append((x, y))

    elif player.facing == "down":
        for y in range(hy + 1, hy + reach + 1):
            for x in range(hx - half_width, hx + half_width + 1):
                tiles.append((x, y))

    elif player.facing == "left":
        for x in range(hx - reach, hx):
            for y in range(hy - half_width, hy + half_width + 1):
                tiles.append((x, y))

    elif player.facing == "right":
        for x in range(hx + 1, hx + reach + 1):
            for y in range(hy - half_width, hy + half_width + 1):
                tiles.append((x, y))

    return tiles

# =========================================================
# 랜덤 몬스터 스폰
# =========================================================
def spawn_monsters_for_room(room_map, player, player_level):
    count = random.randint(2, 3)
    
    monster_classes = [
        ChargerMonster,
        ShooterMonster,
        StabberMonster,
        ExplosionMonster,
        PoisonMonster,
        ]
    weights = [28, 24, 20, 16, 12]

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
def get_tile_sprite(map_manager, x, y):
    tile = map_manager.get_tile(x, y)
    

    if tile != "1":
        return None

    up = safe_get(map_manager, x, y - 1)
    down = safe_get(map_manager, x, y + 1)
    left = safe_get(map_manager, x - 1, y)
    right = safe_get(map_manager, x + 1, y)
    base_inner = pygame.transform.rotate(TILES["inner_corner_tile"], -90)  # ← 여기 숫자 조정

    # =====================
    # 1. 바깥 코너 (가장 중요)
    # =====================
    if up == "0" and left == "0":
        return TILES["edge_tile"]

    if up == "0" and right == "0":
        return pygame.transform.rotate(TILES["edge_tile"], -90)

    if down == "0" and right == "0":
        return pygame.transform.rotate(TILES["edge_tile"], 180)

    if down == "0" and left == "0":
        return pygame.transform.rotate(TILES["edge_tile"], 90)

   # =====================
    # 2. 안쪽 코너
    # =====================
    if up == "1" and left == "1" and safe_get(map_manager, x - 1, y - 1) == "0":
        return base_inner

    if up == "1" and right == "1" and safe_get(map_manager, x + 1, y - 1) == "0":
        return pygame.transform.rotate(base_inner, -90)

    if down == "1" and right == "1" and safe_get(map_manager, x + 1, y + 1) == "0":
        return pygame.transform.rotate(base_inner, 180)

    if down == "1" and left == "1" and safe_get(map_manager, x - 1, y + 1) == "0":
        return pygame.transform.rotate(base_inner, 90)
    # =====================
    # 3. 직선 경계
    # =====================
    if up == "0":
        return TILES["tile"]

    if right == "0":
        return pygame.transform.rotate(TILES["tile"], -90)

    if down == "0":
        return pygame.transform.rotate(TILES["tile"], 180)

    if left == "0":
        return pygame.transform.rotate(TILES["tile"], 90)

    # =====================
    # 4. 기본 바닥
    # =====================
    return TILES["ground"]

def draw_map(game_surface, map_manager):
    for y in range(map_manager.height()):
        for x in range(map_manager.width()):
            rect = tile_rect(x, y)

            # 기본 배경
            pygame.draw.rect(game_surface, (20, 20, 20), rect)

            # 숫자 맵에 맞는 타일 이미지 선택
            sprite = get_tile_sprite(map_manager, x, y)

            if sprite:
                game_surface.blit(sprite, rect.topleft)

def draw_player(surface, player, now):
    visible = True
    if now < player.invincible_until:
        visible = ((now // 80) % 2 == 0)

    if not visible:
        return

    hit_flash = is_player_hit_flash(player, now)

    for i, (x, y) in enumerate(player.body):
        draw_x = x * TILE_SIZE
        draw_y = y * TILE_SIZE

        if i == 0:
            sprite = get_rotated_sprite(PLAYER_HEAD_IMG, player.facing)
        elif i == len(player.body) - 1:
            sprite = get_rotated_sprite(PLAYER_TAIL_IMG, player.facing)
        else:
            sprite = get_rotated_sprite(PLAYER_BODY_IMG, player.facing)

        if sprite:
            sprite_rect = sprite.get_rect(center=(draw_x + TILE_SIZE // 2, draw_y + TILE_SIZE // 2))

            if hit_flash:
                tinted = sprite.copy()
                tinted.fill((255, 120, 120, 90), special_flags=pygame.BLEND_RGBA_ADD)
                surface.blit(tinted, sprite_rect.topleft)
            else:
                surface.blit(sprite, sprite_rect.topleft)
        else:
            rect = pygame.Rect(draw_x, draw_y, TILE_SIZE, TILE_SIZE).inflate(-6, -6)
            color = YELLOW if i == 0 else GREEN
            if i == len(player.body) - 1:
                color = BLUE
            if hit_flash:
                color = (255, 100, 100)

            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

def get_rotated_sprite(sprite, direction):
    if sprite is None:
        return None

    if direction == "up":
        return sprite
    elif direction == "right":
        return pygame.transform.rotate(sprite, -90)
    elif direction == "down":
        return pygame.transform.rotate(sprite, 180)
    elif direction == "left":
        return pygame.transform.rotate(sprite, 90)

    return sprite


def draw_fireballs(surface, fireballs):
    for fb in fireballs:
        pygame.draw.circle(surface, ORANGE, (int(fb.x), int(fb.y)), fb.radius)
        pygame.draw.circle(surface, RED, (int(fb.x), int(fb.y)), fb.radius, 2)

def draw_player_slash_effect(surface, effect_pos, direction, now, effect_until):
    if effect_pos is None or now >= effect_until:
        return

    if not PLAYER_SLASH_FRAMES:
        return

    total_time = 220
    start_time = effect_until - total_time
    elapsed = now - start_time

    if elapsed < 0:
        return

    progress = min(1.0, elapsed / total_time)
    idx = min(len(PLAYER_SLASH_FRAMES) - 1, int(progress * len(PLAYER_SLASH_FRAMES)))
    sprite = PLAYER_SLASH_FRAMES[idx]

    if direction == "up":
        rotated = pygame.transform.rotate(sprite, 90)
    elif direction == "down":
        rotated = pygame.transform.rotate(sprite, -90)
    elif direction == "left":
        rotated = pygame.transform.rotate(sprite, 180)
    else:
        rotated = sprite

    hx, hy = effect_pos
    center_x = hx * TILE_SIZE + TILE_SIZE // 2
    center_y = hy * TILE_SIZE + TILE_SIZE // 2

    if direction == "up":
        center_y -= TILE_SIZE
    elif direction == "down":
        center_y += TILE_SIZE
    elif direction == "left":
        center_x -= TILE_SIZE
    elif direction == "right":
        center_x += TILE_SIZE

    rect = rotated.get_rect(center=(center_x, center_y))
    surface.blit(rotated, rect.topleft)

def draw_enemy_projectiles(surface, enemy_projectiles):
    for ep in enemy_projectiles:
        pygame.draw.circle(surface, (255, 80, 120), (int(ep.x), int(ep.y)), ep.radius)
        pygame.draw.circle(surface, BLACK, (int(ep.x), int(ep.y)), ep.radius, 2)


def draw_attack_tiles(surface, tiles, map_manager):
    for tx, ty in tiles:
        if 0 <= tx < map_manager.width() and 0 <= ty < map_manager.height():
            pygame.draw.rect(surface, WHITE, tile_rect(tx, ty), 3)


def draw_monster_warnings(surface, monsters, map_manager):
    for monster in monsters:
        for tx, ty in getattr(monster, "warning_tiles", []):
            if 0 <= tx < map_manager.width() and 0 <= ty < map_manager.height():
                pygame.draw.rect(surface, RED, tile_rect(tx, ty), 3)

def draw_boss_attack(surface, boss):
    if boss is None or not boss.alive:
        return

    # 경고 타일
    for tx, ty in boss.warning_tiles:
        pygame.draw.rect(surface, ORANGE, tile_rect(tx, ty), 3)

    # 실제 공격 타일
    for tx, ty in boss.attack_tiles:
        pygame.draw.rect(surface, RED, tile_rect(tx, ty), 0)
        pygame.draw.rect(surface, BLACK, tile_rect(tx, ty), 2)

# =========================================================
# UI
# =========================================================
def draw_boss_ui(surface, boss):
    if boss is None or not boss.alive:
        return

    bar_w = 500
    bar_h = 22
    x = (WIDTH - bar_w) // 2
    y = 10

    ratio = boss.hp / boss.max_hp if boss.max_hp > 0 else 0

    pygame.draw.rect(surface, DARK_GRAY, (x, y, bar_w, bar_h))
    pygame.draw.rect(surface, RED, (x, y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(surface, WHITE, (x, y, bar_w, bar_h), 2)

    title = small_font.render("BOSS - THE HAND", True, WHITE)
    surface.blit(title, (x, y - 22))

def draw_player_ui(surface, player, now, total_rooms, room_pos):
    panel_x = 15
    panel_y = GAME_HEIGHT + 8
    panel_w = 410
    panel_h = 118

    pygame.draw.rect(surface, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(surface, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

    hex_center = (panel_x + 55, panel_y + 48)

    hit_flash = is_player_hit_flash(player, now)
    frame_color = RED if hit_flash else WHITE
    draw_hex_frame(surface, hex_center, 38, frame_color, 3)

    # 초상화 상태 결정
    portrait_state = get_portrait_state(player, now)
    portrait = PORTRAITS.get(player.job, {}).get(portrait_state)

    if portrait:
        portrait_rect = portrait.get_rect(center=hex_center)
        surface.blit(portrait, portrait_rect)
    else:
        # 이미지 없을 때 fallback
        char_color = CYAN if player.job == "mage" else GREEN
        if hit_flash:
            char_color = (255, 100, 100)

        pygame.draw.circle(surface, char_color, hex_center, 18)
        pygame.draw.circle(surface, YELLOW, hex_center, 18, 2)
    
    bar_x = panel_x + 110
    hp_y = panel_y + 10
    mp_y = panel_y + 40
    exp_y = panel_y + 70
    bar_w = 210

    hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
    hp_color = GREEN
    if hp_ratio < 0.3 and (now // 200) % 2 == 0:
        hp_color = RED
    if hit_flash:
        hp_color = (255, 90, 90)

    pygame.draw.rect(surface, RED, (bar_x, hp_y, bar_w, 18))
    pygame.draw.rect(surface, hp_color, (bar_x, hp_y, int(bar_w * hp_ratio), 18))

    mp_ratio = player.mp / player.max_mp if player.max_mp > 0 else 0
    pygame.draw.rect(surface, GRAY, (bar_x, mp_y, bar_w, 18))
    pygame.draw.rect(surface, BLUE, (bar_x, mp_y, int(bar_w * mp_ratio), 18))

    exp_ratio = player.exp / player.exp_to_next if player.exp_to_next > 0 else 0
    pygame.draw.rect(surface, GRAY, (bar_x, exp_y, bar_w, 12))
    pygame.draw.rect(surface, YELLOW, (bar_x, exp_y, int(bar_w * exp_ratio), 12))

    text_x = bar_x + bar_w + 12
    surface.blit(small_font.render(f"HP {int(player.hp)}/{player.max_hp}", True, WHITE), (text_x, hp_y - 1))
    surface.blit(small_font.render(f"MP {int(player.mp)}/{player.max_mp}", True, WHITE), (text_x, mp_y - 1))
    surface.blit(small_font.render(f"Lv {player.level}", True, WHITE), (text_x, exp_y - 4))

    info_y = panel_y + 92
    surface.blit(small_font.render(f"직업: {player.job_label}", True, WHITE), (panel_x + 15, info_y))
    surface.blit(small_font.render(f"좌표: {room_pos}", True, WHITE), (panel_x + 120, info_y))
    surface.blit(small_font.render(f"방 수: {total_rooms}", True, WHITE), (panel_x + 240, info_y))


def draw_command_ui(surface, player, now):
    panel_x = 445
    panel_y = GAME_HEIGHT + 8
    panel_w = 320
    panel_h = 118

    pygame.draw.rect(surface, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(surface, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

    title = font.render("SKILL", True, WHITE)
    title_rect = title.get_rect(center=(panel_x + panel_w // 2, panel_y + 18))
    surface.blit(title, title_rect)

    seq = [k.upper() for k, _ in player.command_buffer]
    text = " ".join(seq) if seq else "-"
    cmd_surface = font.render(text, True, CYAN)
    cmd_rect = cmd_surface.get_rect(center=(panel_x + panel_w // 2, panel_y + 52))
    surface.blit(cmd_surface, cmd_rect)

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
    surface.blit(status, status_rect)


def draw_minimap_ui(surface, current_room_pos, visited_rooms):
    panel_x = WIDTH - 145
    panel_y = GAME_HEIGHT + 8
    panel_w = 125
    panel_h = 118

    pygame.draw.rect(surface, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(surface, WHITE, (panel_x, panel_y, panel_w, panel_h), 2)

    title = font.render("MAP", True, WHITE)
    title_rect = title.get_rect(center=(panel_x + panel_w // 2, panel_y + 18))
    surface.blit(title, title_rect)

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
            pygame.draw.line(surface, GRAY, (x1, y1), (x2, y2), 2)

    for room_pos in visited_rooms:
        rx, ry = room_pos
        dx = rx - cur_x
        dy = -(ry - cur_y)

        draw_x = center_x + dx * (minimap_size + gap) - minimap_size // 2
        draw_y = center_y + dy * (minimap_size + gap) - minimap_size // 2

        rect = pygame.Rect(draw_x, draw_y, minimap_size, minimap_size)

        if room_pos == current_room_pos:
            pygame.draw.rect(surface, YELLOW, rect, border_radius=2)
            pygame.draw.rect(surface, BLACK, rect, 1, border_radius=2)
        else:
            pygame.draw.rect(surface, WHITE, rect, border_radius=2)
            pygame.draw.rect(surface, BLACK, rect, 1, border_radius=2)


def draw_full_ui(surface, player, now, visited_rooms, map_manager):
    pygame.draw.rect(surface, BLACK, (0, GAME_HEIGHT, WIDTH, UI_HEIGHT))
    draw_player_ui(surface, player, now, len(map_manager.generated_rooms), map_manager.current_room_pos)
    draw_command_ui(surface, player, now)
    draw_minimap_ui(surface, map_manager.current_room_pos, visited_rooms)


# =========================================================
# 메시지
# =========================================================
def draw_message(surface, text, sub=""):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    title = big_font.render(text, True, WHITE)
    surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

    if sub:
        t2 = font.render(sub, True, WHITE)
        surface.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))


# =========================================================
# 직업 선택
# =========================================================
def select_job():
    while True:
        game_surface.fill(DARK_GRAY)

        title = big_font.render("직업 선택", True, WHITE)
        game_surface.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        warrior_text = font.render("1 : 전사", True, GREEN)
        mage_text = font.render("2 : 마법사", True, CYAN)

        game_surface.blit(warrior_text, warrior_text.get_rect(center=(WIDTH // 2, 240)))
        game_surface.blit(mage_text, mage_text.get_rect(center=(WIDTH // 2, 300)))

        guide1 = small_font.render("전사: 자동 전진 / X 베기 / Space 무적 후 경직", True, WHITE)
        guide2 = small_font.render("마법사: 자동 전진 / 1초 안에 W,W,A,W 후 X", True, WHITE)
        guide3 = small_font.render("방향키 이동 / ESC 종료", True, WHITE)

        game_surface.blit(guide1, guide1.get_rect(center=(WIDTH // 2, 390)))
        game_surface.blit(guide2, guide2.get_rect(center=(WIDTH // 2, 420)))
        game_surface.blit(guide3, guide3.get_rect(center=(WIDTH // 2, 450)))

        present_frame(None, 0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if e.key == pygame.K_1:
                    return "warrior"
                if e.key == pygame.K_2:
                    return "mage"


# =========================================================
# 출력
# =========================================================
def present_frame(player=None, now=0):
    scaled_w, scaled_h = get_scaled_size(SCREEN_WIDTH, SCREEN_HEIGHT, WIDTH, HEIGHT)
    scaled_surface = pygame.transform.scale(game_surface, (scaled_w, scaled_h))

    offset_x = (SCREEN_WIDTH - scaled_w) // 2
    offset_y = (SCREEN_HEIGHT - scaled_h) // 2

    shake_x, shake_y = get_screen_shake_offset(player, now)

    screen.fill(BLACK)
    screen.blit(scaled_surface, (offset_x + shake_x, offset_y + shake_y))
    pygame.display.flip()


# =========================================================
# 메인
# =========================================================
def main():
    job = select_job()

    play_bgm(SOUNDS["game_bgm"], volume=0.4)

    map_manager = MapManager((0, 0))
    player = Player(job, 15, 9)

    # 임시 테스트 아이템
    if player.job == "warrior":
        player.add_item(ITEM_KNIFE)
        player.add_item(ITEM_BOMB)

    monsters = spawn_monsters_for_room(map_manager.current_map, player, player.level)
    fireballs = []
    poison_clouds = []
    enemy_projectiles = []

    visited_rooms = {map_manager.current_room_pos}

    attack_tiles = []
    attack_effect_until = 0
    attack_effect_pos = None
    attack_effect_dir = "right"

    boss = None
    boss_spawned = False

    game_cleared = False

    while True:
        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

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

                    if e.key == pygame.K_x and now >= player.attack_cooldown_until and player.can_act(now) and player.mp >= 25:
                        play_sfx("player_attack")

                        bonus_muscle = player.combo_effects.get("bonus_muscle", 0)
                        final_muscle = player.muscle + bonus_muscle
                        dmg = 5 + (final_muscle * 2) + player.level
                        player.mp -= 25

                        attack_tiles = get_warrior_attack_tiles(player)

                        attack_effect_until = now + 220
                        attack_effect_pos = player.head()
                        attack_effect_dir = player.facing

                        cooldown_mult = player.combo_effects.get("cooldown_mult", 1.0)
                        final_cooldown = int(350 * cooldown_mult)
                        player.attack_cooldown_until = now + final_cooldown

                        for monster in monsters:
                            if (monster.tx, monster.ty) in attack_tiles:
                                play_sfx("hit")
                                monster.hp -= dmg

                                if player.combo_effects.get("bomb_on_hit"):
                                    trigger_explosion(monster.tx, monster.ty, monsters, boss, max(1, dmg // 2))

                        if boss is not None and boss.alive:
                            boss_rect = pygame.Rect(0, 0, TILE_SIZE * 4, TILE_SIZE * 3)
                            boss_rect.center = (int(boss.x), int(boss.y))

                            attack_hit = False
                            for tx, ty in attack_tiles:
                                if boss_rect.colliderect(tile_rect(tx, ty)):
                                    attack_hit = True
                                    break

                            if attack_hit:
                                play_sfx("hit")
                                boss.take_damage(dmg)

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
                            dmg = 10 + (player.intelligence * 2) + player.level

                            if monsters:
                                target = min(monsters, key=lambda m: manhattan(player.head(), (m.tx, m.ty)))
                                fireballs.append(Fireball(player.head(), (target.tx, target.ty), dmg))
                            elif boss is not None and boss.alive:
                                boss_target = (map_manager.width() // 2, 2)
                                fireballs.append(Fireball(player.head(), boss_target, dmg))
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

                    if map_manager.current_room_pos == BOSS_ROOM_POS and player.level >= BOSS_MIN_LEVEL:
                        if not boss_spawned:
                            boss = BossHand(map_manager)
                            boss_spawned = True
                            play_sfx("boss_spawn")
                            play_bgm(SOUNDS["boss_battle"], volume=0.5)
                        monsters = []
                    else:
                        boss = None
                        monsters = spawn_monsters_for_room(map_manager.current_map, player, player.level)

                    fireballs.clear()
                    enemy_projectiles.clear()
                    poison_clouds.clear()
                    attack_tiles.clear()
                    break

        player.regen(dt)

        for monster in monsters:
            monster.update(dt, player, map_manager, now, enemy_projectiles, monsters, boss)

        if boss is not None and boss.alive:
            boss.update(dt, player, now, monsters, boss)

        for ep in enemy_projectiles:
            ep.update(dt, player, map_manager, now, monsters, boss)

        for fb in fireballs:
            fb.update(dt, monsters, map_manager)

        for cloud in poison_clouds:
            cloud.update(dt, player, now, monsters, boss)

        poison_clouds = [cloud for cloud in poison_clouds if cloud.alive]

        if boss is not None and boss.alive:
            boss_rect = pygame.Rect(0, 0, TILE_SIZE * 4, TILE_SIZE * 3)
            boss_rect.center = (int(boss.x), int(boss.y))

            for fb in fireballs:
                if fb.alive and fb.rect().colliderect(boss_rect):
                    boss.take_damage(fb.damage)
                    fb.alive = False

        fireballs = [fb for fb in fireballs if fb.alive]
        enemy_projectiles = [ep for ep in enemy_projectiles if ep.alive]

        new_monsters = []
        for monster in monsters:
            if monster.hp <= 0:
                player.gain_exp(monster.exp_reward)

                if isinstance(monster, PoisonMonster) and not monster.death_poison_spawned:
                    poison_clouds.append(PoisonCloud(monster.tx, monster.ty, radius=2, duration=4.0))
                    monster.death_poison_spawned = True
            else:
                new_monsters.append(monster)

        monsters = new_monsters

        if boss is not None and not boss.alive:
            game_cleared = True

        if boss is None:
            if not monsters:
                monsters = spawn_monsters_for_room(map_manager.current_map, player, player.level)

        if player.hp <= 0:
            while True:
                game_surface.fill(BLACK)
                draw_message(game_surface, "GAME OVER", "R : 재시작 / ESC : 종료")
                present_frame(None, 0)

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_r:
                            main()
                            return
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

        if game_cleared:
            pygame.mixer.music.stop()
            while True:
                game_surface.fill(BLACK)
                draw_message(game_surface, "CLEAR", "R : 다시 시작 / ESC : 종료")
                present_frame(None, 0)

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_r:
                            main()
                            return
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

        game_surface.fill(BLACK)
        draw_map(game_surface, map_manager)

        if now < attack_effect_until:
            draw_attack_tiles(game_surface, attack_tiles, map_manager)

        draw_monster_warnings(game_surface, monsters, map_manager)
        draw_boss_attack(game_surface, boss)

        for monster in monsters:
            monster.draw(game_surface)

        for cloud in poison_clouds:
            cloud.draw(game_surface)

        if boss is not None:
            boss.draw(game_surface)

        draw_enemy_projectiles(game_surface, enemy_projectiles)
        draw_fireballs(game_surface, fireballs)
        draw_player(game_surface, player, now)

        if player.job == "warrior":
            draw_player_slash_effect(game_surface, attack_effect_pos, attack_effect_dir, now, attack_effect_until)

        draw_full_ui(game_surface, player, now, visited_rooms, map_manager)
        draw_boss_ui(game_surface, boss)

        present_frame(player, now)


if __name__ == "__main__":
    main()