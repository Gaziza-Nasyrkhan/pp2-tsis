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

colors = [
    (0,0,0), (255,0,0), (0,255,0),
    (0,0,255), (255,255,0), (255,0,255)
]

color = colors[0]

screen.fill(WHITE)

# State
tool = "pencil"
drawing = False
start_pos = None
last_pos = None
brush_size = 5

# Text
typing = False
text = ""
text_pos = (0, 0)
font = pygame.font.SysFont(None, 30)

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


# MAIN LOOP
while True:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # KEYBOARD
        if event.type == pygame.KEYDOWN:

            # COLORS
            if event.key == pygame.K_1:
                color = colors[0]
            elif event.key == pygame.K_2:
                color = colors[1]
            elif event.key == pygame.K_3:
                color = colors[2]
            elif event.key == pygame.K_4:
                color = colors[3]
            elif event.key == pygame.K_5:
                color = colors[4]
            elif event.key == pygame.K_6:
                color = colors[5]

            # BRUSH SIZE
            if event.key == pygame.K_z:
                brush_size = 2
            elif event.key == pygame.K_x:
                brush_size = 5
            elif event.key == pygame.K_v:
                brush_size = 10

            # TOOLS
            if event.key == pygame.K_p:
                tool = "pencil"
            elif event.key == pygame.K_l:
                tool = "line"
            elif event.key == pygame.K_f:
                tool = "fill"
            elif event.key == pygame.K_t:
                tool = "text"
            elif event.key == pygame.K_r:
                tool = "rectangle"
            elif event.key == pygame.K_c:
                tool = "circle"
            elif event.key == pygame.K_q:
                tool = "square"
            elif event.key == pygame.K_h:
                tool = "rhombus"

            # SAVE
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                filename = datetime.datetime.now().strftime("image_%Y%m%d_%H%M%S.png")
                pygame.image.save(screen, filename)
                print("Saved:", filename)

            # TEXT INPUT
            if typing:
                if event.key == pygame.K_RETURN:
                    img = font.render(text, True, (0,0,0))
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
                flood_fill(screen, x, y, color)

            elif tool == "text":
                typing = True
                text = ""
                text_pos = event.pos

            else:
                start_pos = event.pos

        # MOUSE MOVE
        if event.type == pygame.MOUSEMOTION:

            if tool == "pencil" and drawing:
                pygame.draw.line(screen, color, last_pos, event.pos, brush_size)
                last_pos = event.pos

            elif tool == "line" and start_pos:
                screen.blit(canvas, (0, 0))
                pygame.draw.line(screen, color, start_pos, event.pos, brush_size)

        # MOUSE UP
        if event.type == pygame.MOUSEBUTTONUP:

            if tool == "pencil":
                drawing = False

            elif tool == "line" and start_pos:
                pygame.draw.line(screen, color, start_pos, event.pos, brush_size)
                start_pos = None

            elif tool == "rectangle" and start_pos:
                x1, y1 = start_pos
                x2, y2 = event.pos
                pygame.draw.rect(screen, color,
                                 pygame.Rect(min(x1,x2), min(y1,y2),
                                 abs(x2-x1), abs(y2-y1)), brush_size)
                start_pos = None

            elif tool == "circle" and start_pos:
                x1, y1 = start_pos
                x2, y2 = event.pos
                radius = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
                pygame.draw.circle(screen, color, start_pos, int(radius), brush_size)
                start_pos = None

            elif tool == "square" and start_pos:
                x1, y1 = start_pos
                x2, y2 = event.pos
                side = min(abs(x2-x1), abs(y2-y1))
                pygame.draw.rect(screen, color, pygame.Rect(x1,y1,side,side), brush_size)
                start_pos = None

            elif tool == "rhombus" and start_pos:
                x1, y1 = start_pos
                x2, y2 = event.pos

                pygame.draw.polygon(screen, color, [
                    (x1, y1),
                    ((x1+x2)//2, y1),
                    (x2, y2),
                    ((x1+x2)//2, y2)
                ], brush_size)

                start_pos = None

    pygame.display.flip()
    clock.tick(60)