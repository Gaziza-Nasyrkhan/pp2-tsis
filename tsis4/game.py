import pygame, random, json
from db import save_game, get_best

WIDTH, HEIGHT = 600, 600
TILE = 20

def load_settings():
    with open("settings.json") as f:
        return json.load(f)

def generate_food(snake, walls):
    while True:
        x = random.randrange(0, WIDTH, TILE)
        y = random.randrange(0, HEIGHT, TILE)
        if (x,y) not in snake and (x,y) not in walls:
            return (x,y)

def generate_poison(snake, walls):
    while True:
        x = random.randrange(0, WIDTH, TILE)
        y = random.randrange(0, HEIGHT, TILE)
        if (x,y) not in snake and (x,y) not in walls:
            return (x,y)

def generate_powerup(snake, walls):
    types = ["speed", "slow", "shield"]
    while True:
        x = random.randrange(0, WIDTH, TILE)
        y = random.randrange(0, HEIGHT, TILE)
        if (x,y) not in snake and (x,y) not in walls:
            return {"type": random.choice(types), "pos": (x,y), "time": pygame.time.get_ticks()}

def run_game(screen, username):
    settings = load_settings()
    GREEN = settings["snake_color"]

    snake = [(100,100),(80,100),(60,100)]
    dx, dy = TILE, 0
    walls = []
    level = 1
    speed = 5
    score = 0

    food = generate_food(snake, walls)
    poison = generate_poison(snake, walls)
    power = None
    effect_end = 0
    shield = False

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    best = get_best(username)

    running = True
    while running:
        screen.fill((255,255,255))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and dy == 0: dx,dy = 0,-TILE
                if e.key == pygame.K_DOWN and dy == 0: dx,dy = 0,TILE
                if e.key == pygame.K_LEFT and dx == 0: dx,dy = -TILE,0
                if e.key == pygame.K_RIGHT and dx == 0: dx,dy = TILE,0

        head = (snake[0][0]+dx, snake[0][1]+dy)

        # collision
        if head in snake or head[0]<0 or head[1]<0 or head[0]>=WIDTH or head[1]>=HEIGHT:
            if shield:
                shield = False
            else:
                save_game(username, score, level)
                return "gameover"

        snake.insert(0, head)

        # food
        if head == food:
            score += 1
            food = generate_food(snake, walls)
            if score % 3 == 0:
                level += 1
                speed += 1

        # poison
        elif head == poison:
            snake = snake[:-2]
            if len(snake) <= 1:
                save_game(username, score, level)
                return "gameover"
            poison = generate_poison(snake, walls)

        # power
        elif power and head == power["pos"]:
            if power["type"] == "speed":
                speed += 3
                effect_end = pygame.time.get_ticks() + 5000
            elif power["type"] == "slow":
                speed = max(3, speed-2)
                effect_end = pygame.time.get_ticks() + 5000
            elif power["type"] == "shield":
                shield = True
            power = None

        else:
            snake.pop()

        # power spawn
        if not power and random.randint(1,100) == 1:
            power = generate_powerup(snake, walls)

        # power timeout
        if power and pygame.time.get_ticks() - power["time"] > 8000:
            power = None

        # draw
        for s in snake:
            pygame.draw.rect(screen, GREEN, (*s, TILE, TILE))

        pygame.draw.rect(screen, (255,0,0), (*food, TILE, TILE))
        pygame.draw.rect(screen, (128,0,0), (*poison, TILE, TILE))

        if power:
            color = (0,0,255)
            pygame.draw.rect(screen, color, (*power["pos"], TILE, TILE))

        screen.blit(font.render(f"Score:{score}",1,(0,0,0)), (10,10))
        screen.blit(font.render(f"Best:{best}",1,(0,0,0)), (10,40))

        pygame.display.flip()
        clock.tick(speed)