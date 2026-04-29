import pygame

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)

# ---------------- PENCIL ----------------
def draw_pencil(surface, color, start_pos, end_pos, size):
    pygame.draw.line(surface, color, start_pos, end_pos, size)


# ---------------- LINE ----------------
def draw_line(surface, color, start_pos, end_pos, size):
    pygame.draw.line(surface, color, start_pos, end_pos, size)


# ---------------- RECTANGLE ----------------
def draw_rectangle(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    rect = pygame.Rect(
        min(x1, x2),
        min(y1, y2),
        abs(x2 - x1),
        abs(y2 - y1)
    )

    pygame.draw.rect(surface, color, rect, size)


# ---------------- CIRCLE ----------------
def draw_circle(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    radius = int(((x2 - x1)**2 + (y2 - y1)**2) ** 0.5)

    pygame.draw.circle(surface, color, start_pos, radius, size)


# ---------------- SQUARE ----------------
def draw_square(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    side = min(abs(x2 - x1), abs(y2 - y1))

    rect = pygame.Rect(x1, y1, side, side)

    pygame.draw.rect(surface, color, rect, size)


# ---------------- RHOMBUS ----------------
def draw_rhombus(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    points = [
        (x1, y1),
        ((x1 + x2) // 2, y1),
        (x2, y2),
        ((x1 + x2) // 2, y2)
    ]

    pygame.draw.polygon(surface, color, points, size)


# ---------------- TRIANGLE ----------------
def draw_triangle(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    x3 = x1 - (x2 - x1)
    y3 = y2

    pygame.draw.polygon(surface, color, [
        (x1, y1),
        (x2, y2),
        (x3, y3)
    ], size)


# ---------------- ERASER ----------------
def erase(surface, start_pos, end_pos, size):
    pygame.draw.line(surface, WHITE, start_pos, end_pos, size)


# ---------------- TEXT ----------------
def draw_text(surface, text, pos, color, font):
    img = font.render(text, True, color)
    surface.blit(img, pos)