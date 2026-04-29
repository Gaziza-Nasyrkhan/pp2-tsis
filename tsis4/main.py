import pygame
import random
import sys

from db import (
    init_db,
    get_or_create_player,
    save_result,
    get_leaderboard,
    get_personal_best
)

pygame.init()

WIDTH, HEIGHT = 600, 600
TILE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24)
big = pygame.font.SysFont("Arial", 40)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)


# ---------------- UTIL ----------------

def random_pos(snake):
    while True:
        x = random.randrange(0, WIDTH, TILE)
        y = random.randrange(0, HEIGHT, TILE)
        if (x, y) not in snake:
            return (x, y)


# ---------------- UI ----------------

def username_screen():
    name = ""
    while True:
        screen.fill(WHITE)

        title = big.render("ENTER NAME", True, BLACK)
        screen.blit(title, (200, 150))

        box = pygame.Rect(180, 250, 240, 40)
        pygame.draw.rect(screen, BLACK, box, 2)

        text = font.render(name, True, BLACK)
        screen.blit(text, (box.x + 10, box.y + 8))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name:
                    return name
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15:
                        name += e.unicode


def game_over(screen, score, name):
    while True:
        screen.fill((150, 0, 0))

        t = big.render("GAME OVER", True, WHITE)
        screen.blit(t, (180, 150))

        s = font.render(f"{name} Score: {score}", True, WHITE)
        screen.blit(s, (180, 230))

        r = font.render("Press R to Restart", True, WHITE)
        screen.blit(r, (150, 300))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "restart"


# ---------------- GAME ----------------

def run_game(player_id, name):
    snake = [(100, 100), (80, 100), (60, 100)]
    dx, dy = TILE, 0

    food = random_pos(snake)
    poison = random_pos(snake)

    score = 0
    level = 1
    speed = 6

    while True:
        screen.fill(WHITE)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -TILE
                if e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, TILE
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -TILE, 0
                if e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = TILE, 0

        head = (snake[0][0] + dx, snake[0][1] + dy)

        if head in snake or head[0] < 0 or head[1] < 0 or head[0] >= WIDTH or head[1] >= HEIGHT:
            save_result(player_id, score, level)
            return score, level

        snake.insert(0, head)

        # food
        if head == food:
            score += 1
            food = random_pos(snake)
            if score % 5 == 0:
                level += 1
                speed += 1
        else:
            snake.pop()

        # poison
        if head == poison:
            snake = snake[:-2]
            poison = random_pos(snake)
            if len(snake) <= 1:
                save_result(player_id, score, level)
                return score, level

        # draw snake
        for s in snake:
            pygame.draw.rect(screen, GREEN, (*s, TILE, TILE))

        pygame.draw.rect(screen, RED, (*food, TILE, TILE))
        pygame.draw.rect(screen, (120, 0, 0), (*poison, TILE, TILE))

        hud = font.render(f"Score: {score} Level: {level}", True, BLACK)
        screen.blit(hud, (10, 10))

        pygame.display.flip()
        clock.tick(speed)


# ---------------- MAIN ----------------

def main():
    init_db()

    name = username_screen()
    player_id = get_or_create_player(name)

    best = get_personal_best(player_id)

    while True:
        score, level = run_game(player_id, name)

        best = max(best, score)

        action = game_over(screen, score, name)

        if action == "restart":
            continue


if __name__ == "__main__":
    main()