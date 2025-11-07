import pygame
import sys
import random
import time

# -------- Config --------
WIDTH, HEIGHT = 1100, 600 
DRAW_AREA = (800, HEIGHT)  
PANEL_AREA = (WIDTH - DRAW_AREA[0], HEIGHT)

BG_COLOR = (25, 25, 25)
PANEL_COLOR = (40, 40, 40)
POINT_COLOR = (255, 200, 50)
DDA_COLOR = (50, 200, 255)
BRES_COLOR = (255, 90, 90)
TEXT_COLOR = (230, 230, 230)
ACCENT_COLOR = (180, 180, 180)

BENCH_LINES = 3000
# -------------------------


def dda(surface, x0, y0, x1, y1, color):
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        surface.set_at((int(x0), int(y0)), color)
        return
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x0, y0
    for _ in range(steps + 1):
        surface.set_at((int(round(x)), int(round(y))), color)
        x += x_inc
        y += y_inc


def bresenham(surface, x0, y0, x1, y1, color):
    x0, y0, x1, y1 = map(int, [round(x0), round(y0), round(x1), round(y1)])
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)

    if dy <= dx:
        err, y = dx // 2, y0
        x = x0
        for _ in range(dx + 1):
            surface.set_at((x, y), color)
            x += sx
            err -= dy
            if err < 0:
                y += sy
                err += dx
    else:
        err, x = dy // 2, x0
        y = y0
        for _ in range(dy + 1):
            surface.set_at((x, y), color)
            y += sy
            err -= dx
            if err < 0:
                x += sx
                err += dy


def run_benchmark():
    surf = pygame.Surface(DRAW_AREA)
    pairs = [(random.randint(0, DRAW_AREA[0]-1), random.randint(0, DRAW_AREA[1]-1),
              random.randint(0, DRAW_AREA[0]-1), random.randint(0, DRAW_AREA[1]-1))
             for _ in range(BENCH_LINES)]

    # DDA
    t0 = time.perf_counter()
    for (x0, y0, x1, y1) in pairs:
        dda(surf, x0, y0, x1, y1, (1, 1, 1))
    dda_time = time.perf_counter() - t0

    # Bresenham
    t0 = time.perf_counter()
    for (x0, y0, x1, y1) in pairs:
        bresenham(surf, x0, y0, x1, y1, (1, 1, 1))
    bres_time = time.perf_counter() - t0

    return dda_time, bres_time


def draw_panel(screen, font, small_font, points, bench_result):
    panel_x = DRAW_AREA[0]
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, 0, PANEL_AREA[0], PANEL_AREA[1]))

    # Title
    title = font.render("Line Drawing Demo", True, TEXT_COLOR)
    screen.blit(title, (panel_x + 20, 20))

    subtitle = small_font.render("Compare DDA vs Bresenham", True, ACCENT_COLOR)
    screen.blit(subtitle, (panel_x + 20, 55))

    # Instructions
    y = 100
    instructions = [
        "Controls:",
        "Click 2 points in left area",
        "D - Draw DDA (cyan)",
        "B - Draw Bresenham (red)",
        "A - Draw Both",
        "C - Clear screen",
        "S - Run Benchmark"
    ]
    for line in instructions:
        txt = small_font.render(line, True, TEXT_COLOR)
        screen.blit(txt, (panel_x + 20, y))
        y += 25

    # Show points
    if points:
        y += 10
        screen.blit(font.render("Selected Points:", True, ACCENT_COLOR), (panel_x + 20, y))
        y += 35
        for i, p in enumerate(points[-2:]):
            txt = small_font.render(f"P{i+1}: {p}", True, TEXT_COLOR)
            screen.blit(txt, (panel_x + 20, y))
            y += 25

    # Benchmark results
    if bench_result:
        dda_time, bres_time = bench_result
        y += 30
        screen.blit(font.render("Benchmark:", True, ACCENT_COLOR), (panel_x + 20, y))
        y += 40
        screen.blit(small_font.render(
            f"DDA: {dda_time:.5f} s ({dda_time/BENCH_LINES*1e6:.2f} µs/line)", True, DDA_COLOR), (panel_x + 20, y))
        y += 30
        screen.blit(small_font.render(
            f"Bres: {bres_time:.5f} s ({bres_time/BENCH_LINES*1e6:.2f} µs/line)", True, BRES_COLOR), (panel_x + 20, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DDA vs Bresenham Line Drawing")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24, bold=True)
    small_font = pygame.font.SysFont("consolas", 18)

    draw_surface = pygame.Surface(DRAW_AREA)
    draw_surface.fill(BG_COLOR)

    points = []
    bench_result = None
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if mx < DRAW_AREA[0]: 
                    points.append((mx, my))
                    pygame.draw.circle(draw_surface, POINT_COLOR, (mx, my), 4)
                    if len(points) > 2:
                        points = points[-2:]
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    draw_surface.fill(BG_COLOR)
                    points = []
                    bench_result = None
                elif ev.key == pygame.K_d and len(points) == 2:
                    dda(draw_surface, *points[0], *points[1], DDA_COLOR)
                elif ev.key == pygame.K_b and len(points) == 2:
                    bresenham(draw_surface, *points[0], *points[1], BRES_COLOR)
                elif ev.key == pygame.K_a and len(points) == 2:
                    dda(draw_surface, *points[0], *points[1], DDA_COLOR)
                    bresenham(draw_surface, *points[0], *points[1], BRES_COLOR)
                elif ev.key == pygame.K_s:
                    bench_result = run_benchmark()

        screen.blit(draw_surface, (0, 0))
        draw_panel(screen, font, small_font, points, bench_result)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
