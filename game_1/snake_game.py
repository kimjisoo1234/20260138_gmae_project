import pygame, random, sys, math
pygame.init()

WIDTH, HEIGHT = 800, 600
CELL = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 28)

WHITE, RED, GREEN = (255,255,255),(220,50,50),(50,200,50)
PURPLE = (200,0,200)
GRAY = (40,40,40)
YELLOW = (255,255,0)

# ---------------- 상태 ----------------
snake = [(400,300)]
direction = (CELL,0)

foods = []
monsters = []
projectiles = []

hp = 3
score = 0
difficulty = 1

extra_food_chance = 0.0
shoot_power = 1

# 🔥 피격 시스템
invincible = False
invincible_timer = 0
speed_boost_timer = 0

# ---------------- 함수 ----------------

def spawn_food():
    pos = (random.randrange(0, WIDTH//CELL)*CELL,
           random.randrange(0, HEIGHT//CELL)*CELL)
    foods.append(pos)

def spawn_monster():
    side = random.choice(["top","bottom","left","right"])
    if side=="top":
        x=random.randrange(0,WIDTH//CELL)*CELL; y=-CELL
    elif side=="bottom":
        x=random.randrange(0,WIDTH//CELL)*CELL; y=HEIGHT
    elif side=="left":
        x=-CELL; y=random.randrange(0,HEIGHT//CELL)*CELL
    else:
        x=WIDTH; y=random.randrange(0,HEIGHT//CELL)*CELL
    monsters.append((x,y))

def move_monsters():
    global monsters
    new=[]
    sx,sy = snake[0]
    for mx,my in monsters:
        if sx>mx: mx+=CELL
        elif sx<mx: mx-=CELL
        if sy>my: my+=CELL
        elif sy<my: my-=CELL
        new.append((mx,my))
    monsters=new

# 🔥 락온 발사
def shoot():
    if not monsters:
        return

    px, py = snake[0]
    target = random.choice(monsters)

    dx = target[0] - px
    dy = target[1] - py

    dist = math.hypot(dx, dy)
    if dist == 0: return

    dx /= dist
    dy /= dist

    projectiles.append([px, py, dx*CELL, dy*CELL])

def move_projectiles():
    global projectiles, monsters, score
    new=[]
    for p in projectiles:
        p[0]+=p[2]
        p[1]+=p[3]

        hit=False
        for m in monsters:
            if abs(p[0]-m[0])<CELL and abs(p[1]-m[1])<CELL:
                monsters.remove(m)
                score += 100
                hit=True
                break
        if not hit:
            new.append(p)
    projectiles=new

# 🔥 피격 처리
def take_damage():
    global hp, invincible, invincible_timer, speed_boost_timer

    if invincible:
        return

    hp -= 1
    now = pygame.time.get_ticks()

    invincible = True
    invincible_timer = now
    speed_boost_timer = now

# 🔥 업그레이드 선택
def upgrade_screen():
    global extra_food_chance, shoot_power, snake

    while True:
        screen.fill(GRAY)

        screen.blit(font.render("Choose Upgrade",True,WHITE),(280,200))
        screen.blit(font.render("1: Shoot Power +1",True,WHITE),(250,260))
        screen.blit(font.render("2: Cut Body (-3)",True,WHITE),(250,300))
        screen.blit(font.render("3: More Food Chance",True,WHITE),(250,340))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    shoot_power += 1
                    return
                if e.key == pygame.K_2:
                    if len(snake)>3:
                        snake = snake[:-3]
                    return
                if e.key == pygame.K_3:
                    extra_food_chance += 0.1
                    return

# ---------------- 초기 ----------------
for _ in range(3):
    spawn_food()

monster_tick = 0
monster_delay = 3

# ---------------- 루프 ----------------
while True:
    current_time = pygame.time.get_ticks()

    # 🔥 무적 해제
    if invincible and current_time - invincible_timer > 1000:
        invincible = False

    # 🔥 속도 부스트
    boost = 5 if current_time - speed_boost_timer < 1000 else 0

    difficulty = score//500 + 1
    clock.tick(10 + difficulty + boost)

    # 입력
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key==pygame.K_UP and direction!=(0,CELL):
                direction=(0,-CELL)
            if e.key==pygame.K_DOWN and direction!=(0,-CELL):
                direction=(0,CELL)
            if e.key==pygame.K_LEFT and direction!=(CELL,0):
                direction=(-CELL,0)
            if e.key==pygame.K_RIGHT and direction!=(-CELL,0):
                direction=(CELL,0)

            if e.key==pygame.K_SPACE:
                for _ in range(shoot_power):
                    shoot()

    # 이동
    head = (snake[0][0]+direction[0], snake[0][1]+direction[1])

    # 벽 충돌
    if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT:
        take_damage()
        head = snake[0]

    # 몬스터 충돌
    if head in monsters:
        take_damage()

    if hp <= 0:
        print("GAME OVER")
        pygame.quit(); sys.exit()

    snake.insert(0, head)

    # 먹이
    if head in foods:
        foods.remove(head)
        score += 50

        spawn_food()
        if random.random() < extra_food_chance:
            spawn_food()

        shoot()

        if score % 500 == 0:
            upgrade_screen()
    else:
        snake.pop()

    # 몬스터 생성
    while len(monsters) < difficulty:
        spawn_monster()

    # 몬스터 이동 (느리게)
    monster_tick += 1
    if monster_tick >= monster_delay:
        move_monsters()
        monster_tick = 0

    move_projectiles()

    # 🔥 깜빡임
    draw_snake_flag = True
    if invincible and (current_time//100)%2 == 0:
        draw_snake_flag = False

    # 렌더
    screen.fill(GRAY)

    # snake
    for i, s in enumerate(snake):
        color = YELLOW if i==0 else GREEN
        if draw_snake_flag:
            pygame.draw.rect(screen, color, (*s,CELL,CELL))

    # food
    for f in foods:
        pygame.draw.rect(screen, RED, (*f,CELL,CELL))

    # monsters
    for m in monsters:
        pygame.draw.rect(screen, PURPLE, (*m,CELL,CELL))

    # projectiles
    for p in projectiles:
        pygame.draw.rect(screen, WHITE, (int(p[0]),int(p[1]),CELL//2,CELL//2))

    screen.blit(font.render(f"Score:{score}",True,WHITE),(10,10))
    screen.blit(font.render(f"HP:{hp}",True,WHITE),(10,40))

    pygame.display.flip()
