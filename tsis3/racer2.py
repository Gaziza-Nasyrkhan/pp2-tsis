import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game")
clock = pygame.time.Clock()

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

font = pygame.font.SysFont("Verdana", 24)

# ---------------- PLAYER NAME ----------------
def get_player_name():
    name = ""
    while True:
        screen.fill(WHITE)

        text = font.render("Enter name: " + name, True, BLACK)
        screen.blit(text, (50, 250))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name != "":
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12:
                        name += event.unicode


# ---------------- GAME OVER ----------------
def game_over(score, name):
    while True:
        screen.fill(RED)

        text = font.render(f"GAME OVER | Score: {score}", True, BLACK)
        screen.blit(text, (40, 250))

        text2 = font.render("R - Retry | M - Menu", True, BLACK)
        screen.blit(text2, (60, 300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_m:
                    return "menu"


# ---------------- GAME ----------------
def run_game(name):

    player = pygame.Rect(180, 500, 40, 60)
    enemy = pygame.Rect(random.randint(0, 360), 0, 40, 60)

    speed = 5
    score = 0

    while True:
        clock.tick(FPS)
        screen.fill(WHITE)

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # CONTROLS
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.x < WIDTH - 40:
            player.x += 5

        # ENEMY MOVE
        enemy.y += speed

        if enemy.y > HEIGHT:
            enemy.y = 0
            enemy.x = random.randint(0, 360)
            score += 1

            # speed increase
            if score % 5 == 0:
                speed += 1

        # COLLISION
        if player.colliderect(enemy):
            result = game_over(score, name)
            if result == "retry":
                return run_game(name)
            else:
                return

        # DRAW
        pygame.draw.rect(screen, BLUE, player)
        pygame.draw.rect(screen, RED, enemy)

        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()


# ---------------- START GAME ----------------
player_name = get_player_name()
run_game(player_name)