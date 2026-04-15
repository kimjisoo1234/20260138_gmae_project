import pygame

pygame.init()

# 화면 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Image Move Test")

# 이미지 로드
img = pygame.image.load(r"C:\Users\fande\OneDrive\바탕 화면\school folder\AIgames1\game_1\Game_image\witch.png")

# 🔥 크기 1/4로 축소
img = pygame.transform.scale(img, (img.get_width() // 4, img.get_height() // 4))

# 🔥 화면 중앙 좌표 계산
x = screen_width // 2 - img.get_width() // 2
y = screen_height // 2 - img.get_height() // 2

# 이동 속도
speed = 5

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)  # FPS 제한

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 🔥 키 입력 처리
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        y -= speed
    if keys[pygame.K_s]:
        y += speed
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    # 화면 초기화
    screen.fill((0, 0, 0))

    # 이미지 출력
    screen.blit(img, (x, y))

    pygame.display.update()

pygame.quit()
