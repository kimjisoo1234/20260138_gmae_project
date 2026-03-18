import pygame
import sys
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Color Changing Circle")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)

# 초기 색상
current_color = [0, 0, 255]
target_color = [random.randint(0, 255) for _ in range(3)]

transition_time = 2000  # 2초 (밀리초)
start_time = pygame.time.get_ticks()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 시간 계산
    now = pygame.time.get_ticks()
    elapsed = now - start_time

    # 진행 비율 (0 ~ 1)
    t = min(elapsed / transition_time, 1)

    # 색상 보간 (부드럽게 변화)
    color = [
        int(current_color[i] + (target_color[i] - current_color[i]) * t)
        for i in range(3)
    ]

    # 2초가 지나면 새로운 목표 색 설정
    if t >= 1:
        current_color = target_color
        target_color = [random.randint(0, 255) for _ in range(3)]
        start_time = now

    screen.fill(WHITE)
    pygame.draw.circle(screen, color, (400, 300), 50)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
