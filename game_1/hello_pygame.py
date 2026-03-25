import pygame
import sys
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("OBB / AABB / Circle + Rotation Control")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)

def to_screen_coords(x, y):
    return 400 + x, 300 - y

# ---------------- OBB ----------------
def get_corners(cx, cy, size, angle):
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    h = size / 2
    corners = [(-h,-h),(h,-h),(h,h),(-h,h)]

    result = []
    for x, y in corners:
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        result.append((cx + rx, cy + ry))

    return result

# ---------------- SAT ----------------
def project(axis, points):
    dots = [p[0]*axis[0] + p[1]*axis[1] for p in points]
    return min(dots), max(dots)

def normalize(v):
    length = math.hypot(v[0], v[1])
    return (v[0]/length, v[1]/length)

def get_axes(corners):
    axes = []
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i+1)%4]
        edge = (p2[0]-p1[0], p2[1]-p1[1])
        normal = (-edge[1], edge[0])
        axes.append(normalize(normal))
    return axes

def obb_collision(c1, c2):
    axes = get_axes(c1) + get_axes(c2)
    for axis in axes:
        min1, max1 = project(axis, c1)
        min2, max2 = project(axis, c2)
        if max1 < min2 or max2 < min1:
            return False
    return True

# ---------------- AABB ----------------
def get_aabb(corners):
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return min(xs), min(ys), max(xs), max(ys)

def aabb_collision(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or
                a[3] < b[1] or a[1] > b[3])

# ---------------- Circle ----------------
def circle_collision(c1, r1, c2, r2):
    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    return math.hypot(dx, dy) < (r1 + r2)

# ---------------- 설정 ----------------
box1 = {"x": 100, "y": 0, "angle": 20}
box2 = {"x": -100, "y": 0, "angle": 0}

size = 100
radius = size / 2

# 🔥 회전 속도 변수
rotation_speed = 1.0

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 이동
    if keys[pygame.K_w]: box2["y"] += 3
    if keys[pygame.K_s]: box2["y"] -= 3
    if keys[pygame.K_a]: box2["x"] -= 3
    if keys[pygame.K_d]: box2["x"] += 3

    # 🔥 Z 키로 회전 가속
    if keys[pygame.K_z]:
        rotation_speed += 0.1
    else:
        rotation_speed *= 0.98  # 자연 감속

    # 속도 제한 (선택)
    rotation_speed = max(0.5, min(rotation_speed, 10))

    # 자동 회전
    box2["angle"] -= rotation_speed

    # ---------------- 도형 (회전 X) ----------------
    c1_draw = get_corners(box1["x"], box1["y"], size, 0)
    c2_draw = get_corners(box2["x"], box2["y"], size, 0)

    # ---------------- OBB (회전 O) ----------------
    c1 = get_corners(box1["x"], box1["y"], size, box1["angle"])
    c2 = get_corners(box2["x"], box2["y"], size, box2["angle"])

    # ---------------- AABB (본체 기준) ----------------
    aabb1 = get_aabb(c1_draw)
    aabb2 = get_aabb(c2_draw)

    # ---------------- Circle ----------------
    center1 = (box1["x"], box1["y"])
    center2 = (box2["x"], box2["y"])

    circle_hit = circle_collision(center1, radius, center2, radius)
    aabb_hit = aabb_collision(aabb1, aabb2)
    obb_hit = obb_collision(c1, c2)

    # ---------------- 배경 ----------------
    if obb_hit:
        bg_color = BLACK
    elif aabb_hit:
        bg_color = RED
    elif circle_hit:
        bg_color = YELLOW
    else:
        bg_color = WHITE

    screen.fill(bg_color)

    # ---------------- 좌표 변환 ----------------
    c1_draw_screen = [to_screen_coords(x, y) for x, y in c1_draw]
    c2_draw_screen = [to_screen_coords(x, y) for x, y in c2_draw]

    c1_obb_screen = [to_screen_coords(x, y) for x, y in c1]
    c2_obb_screen = [to_screen_coords(x, y) for x, y in c2]

    # ---------------- 도형 ----------------
    pygame.draw.polygon(screen, GRAY, c1_draw_screen)
    pygame.draw.polygon(screen, GRAY, c2_draw_screen)

    # ---------------- OBB ----------------
    pygame.draw.polygon(screen, GREEN, c1_obb_screen, 2)
    pygame.draw.polygon(screen, GREEN, c2_obb_screen, 2)

    # ---------------- AABB ----------------
    for aabb in [aabb1, aabb2]:
        x1, y1 = to_screen_coords(aabb[0], aabb[3])
        x2, y2 = to_screen_coords(aabb[2], aabb[1])
        rect = pygame.Rect(x1, y1, x2-x1, y2-y1)
        pygame.draw.rect(screen, RED, rect, 2)

    # ---------------- Circle ----------------
    pygame.draw.circle(screen, (255,165,0), to_screen_coords(*center1), int(radius), 2)
    pygame.draw.circle(screen, (255,165,0), to_screen_coords(*center2), int(radius), 2)

    # ---------------- 텍스트 ----------------
    texts = [
        f"Circle Collision: {circle_hit}",
        f"AABB Collision: {aabb_hit}",
        f"OBB Collision: {obb_hit}"
    ]

    text_color = (0,0,0) if bg_color != BLACK else (255,255,255)

    for i, t in enumerate(texts):
        surf = font.render(t, True, text_color)
        screen.blit(surf, (20, 20 + i * 30))

    # 회전 속도 표시 (옵션)
    speed_text = font.render(f"Rotation Speed: {rotation_speed:.2f}", True, text_color)
    screen.blit(speed_text, (20, 120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
