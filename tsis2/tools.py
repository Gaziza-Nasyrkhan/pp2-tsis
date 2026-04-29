import tools
import pygame

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

    rect = pygame.Rect(min(x1, x2), min(y1, y2),
                       abs(x2 - x1), abs(y2 - y1))

    pygame.draw.rect(surface, color, rect, size)


# ---------------- CIRCLE ----------------
def draw_circle(surface, color, start_pos, end_pos, size):
    x1, y1 = start_pos
    x2, y2 = end_pos

    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    pygame.draw.circle(surface, color, start_pos, radius, size)


# ---------------- ERASER ----------------
def erase(surface, start_pos, end_pos, size, bg_color):
    pygame.draw.line(surface, bg_color, start_pos, end_pos, size)


# ---------------- FLOOD FILL ----------------
def flood_fill(surface, x, y, new_color):
    width, height = surface.get_size()
    target_color = surface.get_at((x, y))

    if target_color == new_color:
        return

    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        if surface.get_at((x, y)) == target_color:
            surface.set_at((x, y), new_color)

            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))


# ---------------- TEXT ----------------
def draw_text(surface, text, pos, color, font):
    img = font.render(text, True, color)
    surface.blit(img, pos)