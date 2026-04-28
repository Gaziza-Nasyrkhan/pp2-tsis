import pygame
import sys
import random
import json
import os
from pygame.locals import *

pygame.init()
pygame.mixer.init()

WIDTH = 400
HEIGHT = 600
FPS = 60

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

font_big = pygame.font.SysFont("Verdana", 50)
font_small = pygame.font.SysFont("Verdana", 20)
font_medium = pygame.font.SysFont("Verdana", 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 Racer")
clock = pygame.time.Clock()


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "sound": True,
            "difficulty": "normal",
            "car_color": "red"
        }

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    with open(LEADERBOARD_FILE, "r") as file:
        return json.load(file)


def save_score(name, score, distance, coins):
    data = load_leaderboard()

    data.append({
        "name": name,
        "score": score,
        "distance": distance,
        "coins": coins
    })

    data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]

    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(data, file, indent=4)


settings = load_settings()


background = pygame.image.load("AnimatedStreet.png")
player_img = pygame.transform.scale(pygame.image.load("Player.png"), (60, 100))
enemy_img = pygame.transform.scale(pygame.image.load("Enemy.png"), (60, 100))
coin_img = pygame.transform.scale(pygame.image.load("coiin.png"), (30, 30))

crash_sound = pygame.mixer.Sound("crash.wav")
pygame.mixer.music.load("background.wav")
if settings["sound"]:
    pygame.mixer.music.play(-1)


def draw_text(text, font, color, x, y):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

def get_player_name():
    name = ""
    error = ""
    while True:
        screen.fill(WHITE)
        draw_text("RACER GAME", font_big, BLACK, 60, 80)
        draw_text("Enter your name:", font_medium, BLACK, 80, 200)

        # Input box
        box = pygame.Rect(80, 250, 240, 45)
        pygame.draw.rect(screen, GRAY, box, border_radius=6)
        pygame.draw.rect(screen, BLACK, box, 2, border_radius=6)
        draw_text(name, font_medium, BLACK, 90, 258)

        if error:
            draw_text(error, font_small, RED, 90, 310)

        draw_text("ENTER - Continue", font_small, BLACK, 100, 550)

        pygame.display.update()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if name.strip():
                        return name.strip()
                    else:
                        error = "Name cannot be empty!"
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15:
                        name += event.unicode

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("RACER GAME", font_big, BLACK, 60, 80)

        draw_text("1 - Play", font_medium, BLACK, 120, 220)
        draw_text("2 - Leaderboard", font_medium, BLACK, 70, 280)
        draw_text("3 - Settings", font_medium, BLACK, 90, 340)
        draw_text("4 - Exit", font_medium, BLACK, 120, 400)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_1:
                    return
                elif event.key == K_2:
                    leaderboard_screen()
                elif event.key == K_3:
                    settings_screen()
                elif event.key == K_4:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(FPS)


def leaderboard_screen():
    while True:
        screen.fill(WHITE)
        draw_text("TOP 10", font_big, BLACK, 110, 40)

        data = load_leaderboard()
        y = 130

        for i, item in enumerate(data):
            line = f"{i+1}. {item['name']} - {item['score']}"
            draw_text(line, font_small, BLACK, 40, y)
            y += 35

        draw_text("ESC - Back", font_small, RED, 130, 550)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return

        pygame.display.update()
        clock.tick(FPS)


def settings_screen():
    global settings

    while True:
        screen.fill(WHITE)
        draw_text("SETTINGS", font_big, BLACK, 80, 80)

        sound_text = f"1 - Sound: {'ON' if settings['sound'] else 'OFF'}"
        diff_text = f"2 - Difficulty: {settings['difficulty']}"

        draw_text(sound_text, font_medium, BLACK, 40, 220)
        draw_text(diff_text, font_medium, BLACK, 40, 300)
        draw_text("ESC - Back", font_small, RED, 130, 500)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_1:
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                elif event.key == K_2:
                    if settings["difficulty"] == "easy":
                        settings["difficulty"] = "normal"
                    elif settings["difficulty"] == "normal":
                        settings["difficulty"] = "hard"
                    else:
                        settings["difficulty"] = "easy"
                    save_settings(settings)

                elif event.key == K_ESCAPE:
                    return

        pygame.display.update()
        clock.tick(FPS)


obstacle_img = pygame.Surface((50, 50))
obstacle_img.fill((120, 120, 120))

nitro_img = pygame.Surface((35, 35))
nitro_img.fill((0, 255, 255))

shield_img = pygame.Surface((35, 35))
shield_img.fill((255, 255, 0))

repair_img = pygame.Surface((35, 35))
repair_img.fill((0, 255, 0))


def game_over_screen(score, distance, coins, name="Player"):
    save_score(name, score, distance, coins)

    while True:
        screen.fill(RED)
        draw_text("GAME OVER", font_big, BLACK, 55, 120)
        draw_text(f"Score: {score}", font_medium, BLACK, 110, 250)
        draw_text(f"Distance: {distance}", font_medium, BLACK, 80, 310)
        draw_text(f"Coins: {coins}", font_medium, BLACK, 110, 370)

        draw_text("R - Retry", font_small, BLACK, 130, 470)
        draw_text("M - Menu", font_small, BLACK, 130, 510)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_r:
                    return "retry"
                elif event.key == K_m:
                    return "menu"

        pygame.display.update()
        clock.tick(FPS)


def run_game():
    speed = 5
    score = 0
    coins = 0
    distance = 0

    player_rect = player_img.get_rect(center=(160, 520))
    enemy_rect = enemy_img.get_rect(center=(random.randint(40, WIDTH - 40), 0))
    coin_rect = coin_img.get_rect(center=(random.randint(40, WIDTH - 40), -100))

    coin_value = random.randint(1, 10)

    obstacle_rect = obstacle_img.get_rect(center=(random.randint(40, WIDTH - 40), -200))
    nitro_rect = nitro_img.get_rect(center=(random.randint(40, WIDTH - 40), -400))
    shield_rect = shield_img.get_rect(center=(random.randint(40, WIDTH - 40), -600))
    repair_rect = repair_img.get_rect(center=(random.randint(40, WIDTH - 40), -800))

    active_power = None
    power_timer = 0

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pressed = pygame.key.get_pressed()

        if pressed[K_LEFT] and player_rect.left > 0:
            player_rect.move_ip(-6, 0)
        if pressed[K_RIGHT] and player_rect.right < WIDTH:
            player_rect.move_ip(6, 0)

        enemy_rect.move_ip(0, speed)
        coin_rect.move_ip(0, speed - 2)
        obstacle_rect.move_ip(0, speed)
        nitro_rect.move_ip(0, speed)
        shield_rect.move_ip(0, speed)
        repair_rect.move_ip(0, speed)
        distance += 1

        if enemy_rect.top > HEIGHT:
            score += 1
            enemy_rect.center = (random.randint(40, WIDTH - 40), 0)

        if coin_rect.top > HEIGHT:
            coin_rect.center = (random.randint(40, WIDTH - 40), -100)
            coin_value = random.randint(1, 10)

        if player_rect.colliderect(coin_rect):
            coins += coin_value
            if coins % 5 == 0:
                speed += 1

            coin_rect.center = (random.randint(40, WIDTH - 40), -100)
            coin_value = random.randint(1, 10)

        if obstacle_rect.top > HEIGHT:
            obstacle_rect.center = (random.randint(40, WIDTH - 40), -200)

        if nitro_rect.top > HEIGHT:
            nitro_rect.center = (random.randint(40, WIDTH - 40), -400)

        if shield_rect.top > HEIGHT:
            shield_rect.center = (random.randint(40, WIDTH - 40), -600)

        if repair_rect.top > HEIGHT:
            repair_rect.center = (random.randint(40, WIDTH - 40), -800)

        if player_rect.colliderect(nitro_rect) and active_power is None:
            active_power = "Nitro"
            power_timer = pygame.time.get_ticks()
            speed += 3
            nitro_rect.center = (random.randint(40, WIDTH - 40), -400)

        if player_rect.colliderect(shield_rect) and active_power is None:
            active_power = "Shield"
            shield_rect.center = (random.randint(40, WIDTH - 40), -600)

        if player_rect.colliderect(repair_rect) and active_power is None:
            active_power = "Repair"
            repair_rect.center = (random.randint(40, WIDTH - 40), -800)

        if active_power == "Nitro":
            if pygame.time.get_ticks() - power_timer > 4000:
                speed -= 3
                active_power = None

        if player_rect.colliderect(obstacle_rect):
            if active_power == "Shield":
                active_power = None
                obstacle_rect.center = (random.randint(40, WIDTH - 40), -200)
            elif active_power == "Repair":
                active_power = None
                obstacle_rect.center = (random.randint(40, WIDTH - 40), -200)
            else:
                result = game_over_screen(score, distance, coins, player_name)
                if result == "retry":
                    run_game()
                    return
                else:
                    return

        if player_rect.colliderect(enemy_rect):
            if settings["sound"]:
                pygame.mixer.music.pause()
                crash_sound.play()

            result = game_over_screen(score, distance, coins, player_name)

            if result == "retry":
                run_game()
                return
            else:
                return

        screen.blit(background, (0, 0))
        screen.blit(player_img, player_rect)
        screen.blit(enemy_img, enemy_rect)
        screen.blit(coin_img, coin_rect)
        screen.blit(obstacle_img, obstacle_rect)
        screen.blit(nitro_img, nitro_rect)
        screen.blit(shield_img, shield_rect)
        screen.blit(repair_img, repair_rect)

        draw_text(f"Score: {score}", font_small, BLACK, 10, 10)
        draw_text(f"Coins: {coins}", font_small, BLACK, 280, 10)
        draw_text(f"Distance: {distance}", font_small, BLACK, 130, 40)
        draw_text(str(coin_value), font_small, BLACK, coin_rect.centerx - 5, coin_rect.centery - 25)

        if active_power:
            draw_text(f"Power: {active_power}", font_small, BLUE, 110, 70)

        pygame.display.update()
        clock.tick(FPS)

player_name = get_player_name()

while True:
    main_menu()
    run_game()