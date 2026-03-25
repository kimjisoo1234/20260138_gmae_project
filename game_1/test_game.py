import pygame
import sys
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Inertia Follow Circle")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)

# ======================
# 🎨 색상 관련
# ======================
current_color = [0, 0, 255]
target_color = [random.randint(0, 255) for _ in range(3)]
color_start_time = pygame.time.get_ticks()
color_duration = 2000  # 2초

# ======================
# 🖱 위치 & 물리(관성)
# ======================
current_pos = [400.0, 300.0]
velocity = [0.0, 0.0]

stiffness = 0.04  # 끌어당기는 힘
damping = 0.8     # 마찰

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = pygame.time.get_ticks()

    # ======================
    # 🎨 색상 보간 (2초)
    # ======================
    color_elapsed = now - color_start_time
    t_color = min(color_elapsed / color_duration, 1)

    color = [
        int(current_color[i] + (target_color[i] - current_color[i]) * t_color)
        for i in range(3)
    ]

    if t_color >= 1:
        current_color = target_color
        target_color = [random.randint(0, 255) for _ in range(3)]
        color_start_time = now

    # ======================
    # 🖱 관성 이동 (물리 기반)
    # ======================
    mouse_pos = pygame.mouse.get_pos()

    # 가속도 (마우스로 끌림)
    accel_x = (mouse_pos[0] - current_pos[0]) * stiffness
    accel_y = (mouse_pos[1] - current_pos[1]) * stiffness

    # 속도 업데이트
    velocity[0] += accel_x
    velocity[1] += accel_y

    # 마찰 적용
    velocity[0] *= damping
    velocity[1] *= damping

    # 위치 업데이트
    current_pos[0] += velocity[0]
    current_pos[1] += velocity[1]

    # ======================
    # 화면 그리기
    # ======================
    screen.fill(WHITE)
    pygame.draw.circle(screen, color, (int(current_pos[0]), int(current_pos[1])), 50)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
