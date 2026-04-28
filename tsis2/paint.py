import pygame
import sys
import datetime

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint App")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen.fill(WHITE)

# State
tool = "pencil"  # pencil, line, fill, text
drawing = False
start_pos = None
last_pos = None
brush_size = 5

# Text
typing = False
text = ""
text_pos = (0, 0)
font = pygame.font.SysFont(None, 30)

# For preview
canvas = screen.copy()

# Flood fill
def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return

    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue

        if surface.get_at((x, y)) == target_color:
            surface.set_at((x, y), new_color)

            stack.append((x+1, y))
            stack.append((x-1, y))
            stack.append((x, y+1))
            stack.append((x, y-1))

# Main loop
while True:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # KEYBOARD
        if event.type == pygame.KEYDOWN:

            # Tools
            if event.key == pygame.K_p:
                tool = "pencil"
            if event.key == pygame.K_l:
                tool = "line"
            if event.key == pygame.K_f:
                tool = "fill"
            if event.key == pygame.K_t:
                tool = "text"

            # Brush size
            if event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 10

            # Save Ctrl+S
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                filename = datetime.datetime.now().strftime("image_%Y%m%d_%H%M%S.png")
                pygame.image.save(screen, filename)
                print("Saved:", filename)

            # TEXT INPUT
            if typing:
                if event.key == pygame.K_RETURN:
                    img = font.render(text, True, BLACK)
                    screen.blit(img, text_pos)
                    typing = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    typing = False
                else:
                    text += event.unicode

        # MOUSE DOWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if tool == "pencil":
                drawing = True
                last_pos = event.pos

            elif tool == "line":
                start_pos = event.pos
                canvas = screen.copy()

            elif tool == "fill":
                flood_fill(screen, x, y, BLACK)

            elif tool == "text":
                typing = True
                text = ""
                text_pos = event.pos

        # MOUSE MOTION
        if event.type == pygame.MOUSEMOTION:

            if tool == "pencil" and drawing:
                pygame.draw.line(screen, BLACK, last_pos, event.pos, brush_size)
                last_pos = event.pos

            elif tool == "line" and start_pos:
                screen.blit(canvas, (0, 0))
                pygame.draw.line(screen, BLACK, start_pos, event.pos, brush_size)

        # MOUSE UP
        if event.type == pygame.MOUSEBUTTONUP:

            if tool == "pencil":
                drawing = False

            elif tool == "line" and start_pos:
                pygame.draw.line(screen, BLACK, start_pos, event.pos, brush_size)
                start_pos = None

    pygame.display.flip()
    clock.tick(60)