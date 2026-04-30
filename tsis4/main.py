import pygame
import random
import sys
import os
from db import init_db, get_or_create_player, save_result, get_leaderboard, get_personal_best
from settings import load_settings, save_settings

pygame.init()

WIDTH, HEIGHT = 600, 600
TILE = 20

# ── Colors ──────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GREEN   = (0,   200, 0)
RED     = (220, 0,   0)
GRAY    = (100, 100, 100)
GOLD    = (255, 215, 0)
DARK_RED= (139, 0,   0)   # Poison food
BLUE    = (30,  144, 255)  # Speed boost power-up
CYAN    = (0,   255, 220)  # Slow motion power-up
PURPLE  = (180, 0,   255)  # Shield power-up
BG1     = (255, 255, 255)
BG2     = (212, 212, 212)
PANEL   = (20,  20,  20)
ACCENT  = (50,  200, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game – TSIS 4")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 38, bold=True)
font_med   = pygame.font.SysFont("Arial", 26)
font_small = pygame.font.SysFont("Arial", 20)

# ── Helpers ──────────────────────────────────────────────
def draw_bg(surface):
    for row in range(HEIGHT // TILE):
        for col in range(WIDTH // TILE):
            color = BG1 if (row + col) % 2 == 0 else BG2
            pygame.draw.rect(surface, color, (col * TILE, row * TILE, TILE, TILE))

def draw_text_centered(surface, text, font, color, y):
    surf = font.render(text, True, color)
    surface.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

def draw_button(surface, rect, text, font, bg, fg, border=2):
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, fg, rect, border, border_radius=8)
    txt = font.render(text, True, fg)
    surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                        rect.centery - txt.get_height() // 2))

def load_walls(level):
    path = "levels/level{}.txt".format(level)
    walls = []
    if not os.path.exists(path):
        return walls
    with open(path) as f:
        for r, line in enumerate(f):
            for c, ch in enumerate(line):
                if ch == '#':
                    walls.append((c * TILE, r * TILE))
    return walls

def random_free(snake, walls, exclude=None):
    while True:
        x = random.randrange(0, WIDTH, TILE)
        y = random.randrange(0, HEIGHT, TILE)
        if (x, y) not in snake and (x, y) not in walls:
            if exclude is None or (x, y) != exclude:
                return (x, y)

# ── Username screen ──────────────────────────────────────
def username_screen():
    username = ""
    active = True
    error = ""
    while active:
        screen.fill(PANEL)
        draw_text_centered(screen, "SNAKE GAME", font_big, ACCENT, 120)
        draw_text_centered(screen, "Enter your username:", font_med, WHITE, 210)

        box = pygame.Rect(WIDTH // 2 - 150, 255, 300, 44)
        pygame.draw.rect(screen, WHITE, box, border_radius=6)
        pygame.draw.rect(screen, ACCENT, box, 2, border_radius=6)
        name_surf = font_med.render(username, True, BLACK)
        screen.blit(name_surf, (box.x + 8, box.y + 8))

        if error:
            draw_text_centered(screen, error, font_small, RED, 310)

        draw_text_centered(screen, "Press ENTER to continue", font_small, GRAY, 340)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username.strip():
                        return username.strip()
                    else:
                        error = "Username cannot be empty!"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20:
                        username += event.unicode

# ── Main Menu ────────────────────────────────────────────
def main_menu(username, personal_best):
    buttons = {
        "play":        pygame.Rect(WIDTH//2 - 110, 240, 220, 48),
        "leaderboard": pygame.Rect(WIDTH//2 - 110, 305, 220, 48),
        "settings":    pygame.Rect(WIDTH//2 - 110, 370, 220, 48),
        "quit":        pygame.Rect(WIDTH//2 - 110, 435, 220, 48),
    }
    while True:
        screen.fill(PANEL)
        draw_text_centered(screen, "SNAKE", font_big, ACCENT, 80)
        draw_text_centered(screen, f"Hello, {username}!", font_med, WHITE, 145)
        draw_text_centered(screen, f"Personal Best: {personal_best}", font_small, GOLD, 185)

        mx, my = pygame.mouse.get_pos()
        for key, rect in buttons.items():
            hov = rect.collidepoint(mx, my)
            bg  = ACCENT if hov else (40, 40, 40)
            label = {"play": "▶  Play", "leaderboard": "🏆  Leaderboard",
                     "settings": "⚙  Settings", "quit": "✕  Quit"}[key]
            draw_button(screen, rect, label, font_med, bg, WHITE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return key

# ── Leaderboard screen ───────────────────────────────────
def leaderboard_screen():
    rows = get_leaderboard(10)
    back_btn = pygame.Rect(WIDTH//2 - 80, 545, 160, 40)
    while True:
        screen.fill(PANEL)
        draw_text_centered(screen, "🏆 LEADERBOARD", font_big, GOLD, 30)

        headers = ["#", "Player", "Score", "Level"]
        col_x   = [20, 60, 350, 490]
        for i, h in enumerate(headers):
            s = font_small.render(h, True, GOLD)
            screen.blit(s, (col_x[i], 90))
        pygame.draw.line(screen, GRAY, (20, 112), (580, 112), 1)

        for rank, (uname, score, level) in enumerate(rows, 1):
            y = 120 + (rank - 1) * 38
            color = GOLD if rank == 1 else WHITE
            for i, val in enumerate([str(rank), uname, str(score), str(level)]):
                s = font_small.render(val, True, color)
                screen.blit(s, (col_x[i], y))

        mx, my = pygame.mouse.get_pos()
        hov = back_btn.collidepoint(mx, my)
        draw_button(screen, back_btn, "← Back", font_med, ACCENT if hov else (40,40,40), WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

# ── Settings screen ──────────────────────────────────────
def settings_screen(cfg):
    colors_list = [
        ("Green",  [0, 200, 0]),
        ("Blue",   [0, 100, 255]),
        ("Yellow", [255, 220, 0]),
        ("White",  [240, 240, 240]),
    ]
    color_idx = 0
    for i, (n, c) in enumerate(colors_list):
        if c == cfg["snake_color"]:
            color_idx = i

    back_btn  = pygame.Rect(WIDTH//2 - 80, 500, 160, 40)
    left_btn  = pygame.Rect(WIDTH//2 - 140, 250, 40, 36)
    right_btn = pygame.Rect(WIDTH//2 + 100, 250, 40, 36)

    while True:
        screen.fill(PANEL)
        draw_text_centered(screen, "⚙  Settings", font_big, WHITE, 40)

        # Snake color
        draw_text_centered(screen, "Snake Color", font_med, GRAY, 210)
        cname, cval = colors_list[color_idx]
        pygame.draw.rect(screen, tuple(cval), (WIDTH//2 - 55, 250, 110, 36), border_radius=6)
        draw_button(screen, left_btn,  "◀", font_med, (40,40,40), WHITE)
        draw_button(screen, right_btn, "▶", font_med, (40,40,40), WHITE)
        draw_text_centered(screen, cname, font_small, WHITE, 295)

        # Grid overlay toggle
        go_rect = pygame.Rect(WIDTH//2 - 60, 340, 120, 36)
        go_col  = ACCENT if cfg["grid_overlay"] else (60,60,60)
        draw_button(screen, go_rect,
                    "Grid: ON" if cfg["grid_overlay"] else "Grid: OFF",
                    font_med, go_col, WHITE)

        # Sound toggle
        snd_rect = pygame.Rect(WIDTH//2 - 60, 395, 120, 36)
        snd_col  = ACCENT if cfg["sound"] else (60,60,60)
        draw_button(screen, snd_rect,
                    "Sound: ON" if cfg["sound"] else "Sound: OFF",
                    font_med, snd_col, WHITE)

        mx, my = pygame.mouse.get_pos()
        hov = back_btn.collidepoint(mx, my)
        draw_button(screen, back_btn, "← Back", font_med, ACCENT if hov else (40,40,40), WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if left_btn.collidepoint(event.pos):
                    color_idx = (color_idx - 1) % len(colors_list)
                    cfg["snake_color"] = colors_list[color_idx][1]
                    save_settings(cfg)
                elif right_btn.collidepoint(event.pos):
                    color_idx = (color_idx + 1) % len(colors_list)
                    cfg["snake_color"] = colors_list[color_idx][1]
                    save_settings(cfg)
                elif go_rect.collidepoint(event.pos):
                    cfg["grid_overlay"] = not cfg["grid_overlay"]
                    save_settings(cfg)
                elif snd_rect.collidepoint(event.pos):
                    cfg["sound"] = not cfg["sound"]
                    save_settings(cfg)
                elif back_btn.collidepoint(event.pos):
                    return cfg
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return cfg

# ── Game Over screen ─────────────────────────────────────
def game_over_screen(score, level, personal_best):
    play_btn = pygame.Rect(WIDTH//2 - 110, 330, 220, 48)
    menu_btn = pygame.Rect(WIDTH//2 - 110, 395, 220, 48)
    lb_btn   = pygame.Rect(WIDTH//2 - 110, 460, 220, 48)

    while True:
        screen.fill((80, 0, 0))
        draw_text_centered(screen, "GAME OVER", font_big, WHITE, 100)
        draw_text_centered(screen, f"Score: {score}    Level: {level}", font_med, WHITE, 180)
        pb_color = GOLD if score >= personal_best else GRAY
        draw_text_centered(screen, f"Personal Best: {personal_best}", font_small, pb_color, 230)
        if score >= personal_best and score > 0:
            draw_text_centered(screen, "🎉 New Record!", font_med, GOLD, 265)

        mx, my = pygame.mouse.get_pos()
        for btn, label in [(play_btn, "▶  Play Again"), (menu_btn, "⌂  Main Menu"), (lb_btn, "🏆  Leaderboard")]:
            hov = btn.collidepoint(mx, my)
            draw_button(screen, btn, label, font_med, ACCENT if hov else (60,0,0), WHITE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.collidepoint(event.pos):
                    return "play"
                if menu_btn.collidepoint(event.pos):
                    return "menu"
                if lb_btn.collidepoint(event.pos):
                    return "leaderboard"

# ── Power-up logic ───────────────────────────────────────
POWERUP_TYPES = [
    {"type": "speed_boost",  "color": BLUE,   "duration": 5000, "label": "SPEED!"},
    {"type": "slow_motion",  "color": CYAN,   "duration": 5000, "label": "SLOW"},
    {"type": "shield",       "color": PURPLE, "duration": 0,    "label": "SHIELD"},
]

def spawn_powerup(snake, walls, food, disfood, poison):
    while True:
        x = random.randrange(0, WIDTH, TILE)
        y = random.randrange(0, HEIGHT, TILE)
        pos = (x, y)
        occupied = set(snake) | set(walls) | {food}
        if disfood: occupied.add(disfood["pos"])
        if poison:  occupied.add(poison["pos"])
        if pos not in occupied:
            pt = random.choice(POWERUP_TYPES)
            return {"pos": pos, "type": pt["type"],
                    "color": pt["color"], "label": pt["label"],
                    "duration": pt["duration"],
                    "spawn_time": pygame.time.get_ticks()}

# ── Main game loop ───────────────────────────────────────
def run_game(username, player_id, cfg):
    def make_disfood(snake, walls, food_pos):
        pos = random_free(snake, walls, exclude=food_pos)
        return {"pos": pos, "value": 5, "color": GOLD,
                "spawn_time": pygame.time.get_ticks()}

    def make_poison(snake, walls, food_pos, disfood):
        exclude_set = set(snake) | set(walls) | {food_pos}
        if disfood: exclude_set.add(disfood["pos"])
        while True:
            x = random.randrange(0, WIDTH, TILE)
            y = random.randrange(0, HEIGHT, TILE)
            if (x, y) not in exclude_set:
                return {"pos": (x, y), "color": DARK_RED,
                        "spawn_time": pygame.time.get_ticks()}

    def reset():
        snake = [(100, 100), (80, 100), (60, 100)]
        dx, dy = TILE, 0
        level  = 1
        walls  = load_walls(level)
        food   = random_free(snake, walls)
        dis    = make_disfood(snake, walls, food)
        poi    = make_poison(snake, walls, food, dis)
        score  = 0
        base_speed = 5
        return snake, dx, dy, food, dis, poi, score, level, base_speed, walls

    snake, dx, dy, food, disfood, poison, score, level, base_speed, walls = reset()

    active_powerup   = None
    powerup_obj      = None
    shield_active    = False
    powerup_next     = pygame.time.get_ticks() + random.randint(8000, 15000)

    FOOD_LIFETIME    = 5000
    POISON_LIFETIME  = 8000
    DISF_LIFETIME    = 5000
    last_dis_change  = pygame.time.get_ticks()

    personal_best = get_personal_best(player_id)
    game_over = False

    while True:
        now = pygame.time.get_ticks()

        # ── Events ──────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP    and dy == 0:  dx, dy = 0, -TILE
                if event.key == pygame.K_DOWN  and dy == 0:  dx, dy = 0,  TILE
                if event.key == pygame.K_LEFT  and dx == 0:  dx, dy = -TILE, 0
                if event.key == pygame.K_RIGHT and dx == 0:  dx, dy =  TILE, 0

        if game_over:
            break

        # ── Disappearing food timer ──────────────────────
        if now - last_dis_change >= DISF_LIFETIME:
            disfood = make_disfood(snake, walls, food)
            last_dis_change = now

        # ── Poison timer ────────────────────────────────
        if now - poison["spawn_time"] >= POISON_LIFETIME:
            poison = make_poison(snake, walls, food, disfood)

        # ── Power-up spawn timer ─────────────────────────
        if powerup_obj is None and now >= powerup_next:
            powerup_obj = spawn_powerup(snake, walls, food, disfood, poison)

        # ── Power-up disappear after 8 sec ───────────────
        if powerup_obj and now - powerup_obj["spawn_time"] >= 8000:
            powerup_obj = None
            powerup_next = now + random.randint(8000, 15000)

        # ── Active power-up expiry ───────────────────────
        if active_powerup and active_powerup["duration"] > 0:
            if now - active_powerup["start"] >= active_powerup["duration"]:
                active_powerup = None
                shield_active  = False

        # ── Effective speed ──────────────────────────────
        speed = base_speed
        if active_powerup:
            if active_powerup["type"] == "speed_boost": speed = base_speed + 4
            if active_powerup["type"] == "slow_motion": speed = max(2, base_speed - 3)

        # ── Move snake ──────────────────────────────────
        head = (snake[0][0] + dx, snake[0][1] + dy)

        # ── Collision checks ─────────────────────────────
        hit_wall   = head in walls
        hit_border = head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT
        hit_self   = head in snake

        if shield_active and (hit_wall or hit_border):
            # Shield: ignore wall/border once, teleport to random free spot
            head = random_free(snake, walls)
            shield_active = False
            active_powerup = None
        elif hit_border or hit_wall or hit_self:
            game_over = True
            break

        # ── Poison check ─────────────────────────────────
        if head == poison["pos"]:
            # Chomp by 2 segments, game over if too short
            snake = snake[2:] if len(snake) > 3 else snake
            if len(snake) <= 1:
                game_over = True
                break
            poison = make_poison(snake, walls, food, disfood)
            snake.insert(0, head)
            snake.pop()
            # Redraw and continue
        else:
            snake.insert(0, head)

            grew = False
            # ── Normal food ──────────────────────────────
            if head == food:
                val = random.randint(1, 3)
                score += val
                grew = True
                food = random_free(snake, walls, exclude=disfood["pos"])
                if score % 5 == 0:
                    level += 1
                    base_speed += 1
                    walls = load_walls(level)

            # ── Disappearing food ────────────────────────
            elif head == disfood["pos"]:
                score += disfood["value"]
                grew = True
                disfood = make_disfood(snake, walls, food)
                last_dis_change = now
                if score % 5 == 0:
                    level += 1
                    base_speed += 1
                    walls = load_walls(level)

            # ── Power-up ─────────────────────────────────
            elif powerup_obj and head == powerup_obj["pos"]:
                pt = powerup_obj["type"]
                active_powerup = {"type": pt, "duration": powerup_obj["duration"],
                                  "start": now, "label": powerup_obj["label"]}
                if pt == "shield":
                    shield_active = True
                powerup_obj  = None
                powerup_next = now + random.randint(8000, 15000)

            if not grew:
                snake.pop()

        # ── Draw ─────────────────────────────────────────
        draw_bg(screen)

        if cfg.get("grid_overlay"):
            for gx in range(0, WIDTH, TILE):
                pygame.draw.line(screen, (180, 180, 180), (gx, 0), (gx, HEIGHT))
            for gy in range(0, HEIGHT, TILE):
                pygame.draw.line(screen, (180, 180, 180), (0, gy), (WIDTH, gy))

        # Walls
        for w in walls:
            pygame.draw.rect(screen, GRAY, (*w, TILE, TILE))
            pygame.draw.rect(screen, (60, 60, 60), (*w, TILE, TILE), 1)

        # Snake
        sc = tuple(cfg["snake_color"])
        for i, seg in enumerate(snake):
            color = tuple(min(255, c + 40) for c in sc) if i == 0 else sc
            pygame.draw.rect(screen, color, (*seg, TILE, TILE))
            pygame.draw.rect(screen, (0, 80, 0), (*seg, TILE, TILE), 1)

        # Foods
        pygame.draw.rect(screen, RED,     (*food, TILE, TILE))
        pygame.draw.rect(screen, GOLD,    (*disfood["pos"], TILE, TILE))
        pygame.draw.rect(screen, DARK_RED,(*poison["pos"],  TILE, TILE))

        # Power-up on field
        if powerup_obj:
            pygame.draw.rect(screen, powerup_obj["color"], (*powerup_obj["pos"], TILE, TILE))
            pygame.draw.rect(screen, WHITE, (*powerup_obj["pos"], TILE, TILE), 2)

        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 160), (0, 0, WIDTH, 36))
        hud = font_small.render(f"Score: {score}   Level: {level}   PB: {personal_best}   User: {username}", True, WHITE)
        screen.blit(hud, (8, 8))

        # Active power-up indicator
        if active_powerup:
            ind = font_small.render(f"⚡ {active_powerup['label']}", True, GOLD)
            screen.blit(ind, (8, 575))
            if active_powerup["duration"] > 0:
                elapsed  = now - active_powerup["start"]
                fraction = 1 - elapsed / active_powerup["duration"]
                pygame.draw.rect(screen, GOLD,  (0, 595, int(WIDTH * fraction), 5))

        # Shield indicator
        if shield_active:
            sh = font_small.render("🛡 SHIELD ACTIVE", True, PURPLE)
            screen.blit(sh, (WIDTH - sh.get_width() - 8, 575))

        pygame.display.flip()
        clock.tick(speed)

    # ── Game Over ────────────────────────────────────────
    personal_best = max(personal_best, score)
    save_result(player_id, score, level)
    return score, level, personal_best

# ── Entry point ──────────────────────────────────────────
def main():
    init_db()
    cfg      = load_settings()
    username = username_screen()
    player_id = get_or_create_player(username)
    personal_best = get_personal_best(player_id)

    action = "menu"
    while True:
        if action == "menu":
            personal_best = get_personal_best(player_id)
            action = main_menu(username, personal_best)

        elif action == "play":
            score, level, personal_best = run_game(username, player_id, cfg)
            action = game_over_screen(score, level, personal_best)

        elif action == "leaderboard":
            leaderboard_screen()
            action = "menu"

        elif action == "settings":
            cfg = settings_screen(cfg)
            action = "menu"

        elif action == "quit":
            pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()