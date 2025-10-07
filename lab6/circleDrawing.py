import pygame
import sys
import random
import time

# -------- Config --------
WIDTH, HEIGHT = 1200, 650  
DRAW_AREA = (800, HEIGHT)  
PANEL_AREA = (WIDTH - DRAW_AREA[0], HEIGHT)

BG_COLOR = (25, 25, 25)
PANEL_COLOR = (40, 40, 40)
CENTER_COLOR = (255, 200, 50)
MIDPOINT_COLOR = (50, 200, 255)
BRES_COLOR = (255, 90, 90)
TEXT_COLOR = (230, 230, 230)
ACCENT_COLOR = (180, 180, 180)

BENCH_CIRCLES = 1000
# -------------------------


def plot_circle_points(surface, xc, yc, x, y, color):
    """Plot 8 symmetrical points of a circle"""
    points = [
        (xc + x, yc + y), (xc - x, yc + y),
        (xc + x, yc - y), (xc - x, yc - y),
        (xc + y, yc + x), (xc - y, yc + x),
        (xc + y, yc - x), (xc - y, yc - x)
    ]
    for px, py in points:
        if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
            surface.set_at((int(px), int(py)), color)


def midpoint_circle(surface, xc, yc, r, color):
    """Midpoint Circle Drawing Algorithm"""
    x = 0
    y = r
    p = 1 - r  # Initial decision parameter
    
    plot_circle_points(surface, xc, yc, x, y, color)
    
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        plot_circle_points(surface, xc, yc, x, y, color)


def bresenham_circle(surface, xc, yc, r, color):
    """Bresenham's Circle Drawing Algorithm"""
    x = 0
    y = r
    d = 3 - 2 * r  # Initial decision parameter
    
    plot_circle_points(surface, xc, yc, x, y, color)
    
    while x <= y:
        x += 1
        if d < 0:
            d += 4 * x + 6
        else:
            y -= 1
            d += 4 * (x - y) + 10
        plot_circle_points(surface, xc, yc, x, y, color)


def run_benchmark():
    """Benchmark both algorithms with random circles"""
    surf = pygame.Surface(DRAW_AREA)
    circles = [(random.randint(50, DRAW_AREA[0]-50), 
                random.randint(50, DRAW_AREA[1]-50),
                random.randint(20, 100))
               for _ in range(BENCH_CIRCLES)]

    # Midpoint
    t0 = time.perf_counter()
    for (xc, yc, r) in circles:
        midpoint_circle(surf, xc, yc, r, (1, 1, 1))
    midpoint_time = time.perf_counter() - t0

    # Bresenham
    t0 = time.perf_counter()
    for (xc, yc, r) in circles:
        bresenham_circle(surf, xc, yc, r, (1, 1, 1))
    bres_time = time.perf_counter() - t0

    return midpoint_time, bres_time


def draw_panel(screen, font, small_font, center, radius, bench_result):
    """Draw the control panel on the right side"""
    panel_x = DRAW_AREA[0]
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, 0, PANEL_AREA[0], PANEL_AREA[1]))

    # Title
    title = font.render("Circle Drawing Demo", True, TEXT_COLOR)
    screen.blit(title, (panel_x + 20, 20))

    subtitle = small_font.render("Midpoint vs Bresenham", True, ACCENT_COLOR)
    screen.blit(subtitle, (panel_x + 20, 55))

    # Instructions
    y = 100
    instructions = [
        "Controls:",
        "Click to set center (yellow)",
        "Mouse wheel: ±5 radius",
        "Shift+wheel: ±1 radius",
        "UP/DOWN: ±5, Shift: ±1",
        "",
        "M - Draw Midpoint (cyan)",
        "B - Draw Bresenham (red)",
        "A - Draw Both (overlapped)",
        "C - Clear screen",
        "S - Run Benchmark"
    ]
    for line in instructions:
        txt = small_font.render(line, True, TEXT_COLOR)
        screen.blit(txt, (panel_x + 20, y))
        y += 25

    # Show center and radius
    if center:
        y += 10
        screen.blit(font.render("Circle Parameters:", True, ACCENT_COLOR), (panel_x + 20, y))
        y += 35
        txt = small_font.render(f"Center: {center}", True, TEXT_COLOR)
        screen.blit(txt, (panel_x + 20, y))
        y += 25
        txt = small_font.render(f"Radius: {radius}", True, TEXT_COLOR)
        screen.blit(txt, (panel_x + 20, y))

    # Benchmark results
    if bench_result:
        mid_time, bres_time = bench_result
        y += 30
        screen.blit(font.render("Benchmark:", True, ACCENT_COLOR), (panel_x + 20, y))
        y += 40
        screen.blit(small_font.render(
            f"Midpoint: {mid_time:.5f} s", True, MIDPOINT_COLOR), (panel_x + 20, y))
        y += 25
        screen.blit(small_font.render(
            f"({mid_time/BENCH_CIRCLES*1e6:.2f} µs/circle)", True, MIDPOINT_COLOR), (panel_x + 20, y))
        y += 35
        screen.blit(small_font.render(
            f"Bresenham: {bres_time:.5f} s", True, BRES_COLOR), (panel_x + 20, y))
        y += 25
        screen.blit(small_font.render(
            f"({bres_time/BENCH_CIRCLES*1e6:.2f} µs/circle)", True, BRES_COLOR), (panel_x + 20, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Midpoint vs Bresenham Circle Drawing")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24, bold=True)
    small_font = pygame.font.SysFont("consolas", 18)

    draw_surface = pygame.Surface(DRAW_AREA)
    draw_surface.fill(BG_COLOR)

    center = None
    radius = 50
    bench_result = None
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                if ev.button == 1 and mx < DRAW_AREA[0]:  # Left click in draw area
                    center = (mx, my)
                    draw_surface.fill(BG_COLOR)
                    # Draw center point
                    pygame.draw.circle(draw_surface, CENTER_COLOR, center, 5)
                    bench_result = None
                
                elif ev.button == 4:  # Mouse wheel up
                    mods = pygame.key.get_mods()
                    increment = 1 if mods & pygame.KMOD_SHIFT else 5
                    radius = min(radius + increment, 300)
                elif ev.button == 5:  # Mouse wheel down
                    mods = pygame.key.get_mods()
                    decrement = 1 if mods & pygame.KMOD_SHIFT else 5
                    radius = max(radius - decrement, 1)
            
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    draw_surface.fill(BG_COLOR)
                    center = None
                    radius = 50
                    bench_result = None
                
                elif ev.key == pygame.K_UP:
                    mods = pygame.key.get_mods()
                    increment = 1 if mods & pygame.KMOD_SHIFT else 5
                    radius = min(radius + increment, 300)
                elif ev.key == pygame.K_DOWN:
                    mods = pygame.key.get_mods()
                    decrement = 1 if mods & pygame.KMOD_SHIFT else 5
                    radius = max(radius - decrement, 1)
                
                elif ev.key == pygame.K_m and center:
                    midpoint_circle(draw_surface, center[0], center[1], radius, MIDPOINT_COLOR)
                
                elif ev.key == pygame.K_b and center:
                    bresenham_circle(draw_surface, center[0], center[1], radius, BRES_COLOR)
                
                elif ev.key == pygame.K_a and center:
                    midpoint_circle(draw_surface, center[0], center[1], radius, MIDPOINT_COLOR)
                    bresenham_circle(draw_surface, center[0], center[1], radius, BRES_COLOR)
                
                elif ev.key == pygame.K_s:
                    bench_result = run_benchmark()

        screen.blit(draw_surface, (0, 0))
        draw_panel(screen, font, small_font, center, radius, bench_result)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()