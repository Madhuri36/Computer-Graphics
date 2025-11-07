import pygame
import sys
import time
from collections import deque

# -------- Config --------
WIDTH, HEIGHT = 1100, 650
DRAW_AREA = (800, HEIGHT)
PANEL_AREA = (WIDTH - DRAW_AREA[0], HEIGHT)

BG_COLOR = (25, 25, 25)
PANEL_COLOR = (40, 40, 40)
POLYGON_COLOR = (255, 200, 50)

# Different colors for each algorithm
SCANLINE_COLOR = (100, 255, 150)      # Green
FLOOD4_COLOR = (100, 150, 255)        # Blue
FLOOD8_COLOR = (255, 100, 255)        # Magenta
BOUNDARY_FILL_COLOR = (255, 200, 100) # Orange
BOUNDARY_OUTLINE = (255, 50, 50)      # Red

TEXT_COLOR = (230, 230, 230)
ACCENT_COLOR = (180, 180, 180)
VERTEX_COLOR = (255, 255, 100)
# -------------------------


def draw_line_bresenham(surface, x0, y0, x1, y1, color):
    """Draw a line using Bresenham's algorithm"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        if 0 <= x0 < surface.get_width() and 0 <= y0 < surface.get_height():
            surface.set_at((x0, y0), color)
        
        if x0 == x1 and y0 == y1:
            break
        
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def scanline_fill(surface, polygon, fill_color):
    """Scanline Fill Algorithm"""
    if len(polygon) < 3:
        return 0
    
    pixels_filled = 0
    
    # Find y bounds
    min_y = min(p[1] for p in polygon)
    max_y = max(p[1] for p in polygon)
    
    # For each scanline
    for y in range(min_y, max_y + 1):
        intersections = []
        
        # Find intersections with polygon edges
        n = len(polygon)
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            
            # Check if edge crosses scanline
            if y1 == y2:  # Horizontal edge
                continue
            
            if min(y1, y2) <= y < max(y1, y2):
                # Calculate x intersection
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(int(x))
        
        # Sort intersections
        intersections.sort()
        
        # Fill between pairs
        for i in range(0, len(intersections) - 1, 2):
            x_start = intersections[i]
            x_end = intersections[i + 1]
            for x in range(x_start, x_end + 1):
                if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
                    surface.set_at((x, y), fill_color)
                    pixels_filled += 1
    
    return pixels_filled


def flood_fill_4(surface, x, y, fill_color, target_color):
    """4-connected Flood Fill using BFS"""
    if x < 0 or x >= surface.get_width() or y < 0 or y >= surface.get_height():
        return 0
    
    start_color = surface.get_at((x, y))[:3]
    if start_color == fill_color or start_color != target_color:
        return 0
    
    pixels_filled = 0
    queue = deque([(x, y)])
    visited = set()
    
    while queue:
        cx, cy = queue.popleft()
        
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= surface.get_width() or cy < 0 or cy >= surface.get_height():
            continue
        
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        
        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))
        pixels_filled += 1
        
        # 4-connected neighbors
        queue.append((cx + 1, cy))
        queue.append((cx - 1, cy))
        queue.append((cx, cy + 1))
        queue.append((cx, cy - 1))
    
    return pixels_filled


def flood_fill_8(surface, x, y, fill_color, target_color):
    """8-connected Flood Fill using BFS"""
    if x < 0 or x >= surface.get_width() or y < 0 or y >= surface.get_height():
        return 0
    
    start_color = surface.get_at((x, y))[:3]
    if start_color == fill_color or start_color != target_color:
        return 0
    
    pixels_filled = 0
    queue = deque([(x, y)])
    visited = set()
    
    while queue:
        cx, cy = queue.popleft()
        
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= surface.get_width() or cy < 0 or cy >= surface.get_height():
            continue
        
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        
        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))
        pixels_filled += 1
        
        # 8-connected neighbors
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    queue.append((cx + dx, cy + dy))
    
    return pixels_filled


def boundary_fill(surface, x, y, fill_color, boundary_color):
    """Boundary Fill Algorithm (4-connected)"""
    if x < 0 or x >= surface.get_width() or y < 0 or y >= surface.get_height():
        return 0
    
    current_color = surface.get_at((x, y))[:3]
    if current_color == fill_color or current_color == boundary_color:
        return 0
    
    pixels_filled = 0
    stack = [(x, y)]
    visited = set()
    
    while stack:
        cx, cy = stack.pop()
        
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= surface.get_width() or cy < 0 or cy >= surface.get_height():
            continue
        
        pixel_color = surface.get_at((cx, cy))[:3]
        if pixel_color == boundary_color or pixel_color == fill_color:
            continue
        
        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))
        pixels_filled += 1
        
        # 4-connected neighbors
        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))
    
    return pixels_filled


def draw_polygon(surface, vertices, color, thickness=2):
    """Draw polygon outline with thickness to prevent gaps"""
    if len(vertices) < 2:
        return
    
    for i in range(len(vertices)):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % len(vertices)]
        
        # Draw thicker lines to prevent gaps
        draw_line_bresenham(surface, x1, y1, x2, y2, color)
        
        # Add extra pixels around each line to ensure no gaps
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx*dx + dy*dy <= thickness*thickness:
                    draw_line_bresenham(surface, x1+dx, y1+dy, x2+dx, y2+dy, color)
        
        # Extra reinforcement at vertices to close gaps
        for dx in range(-thickness-1, thickness+2):
            for dy in range(-thickness-1, thickness+2):
                if dx*dx + dy*dy <= (thickness+1)*(thickness+1):
                    px, py = x1 + dx, y1 + dy
                    if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                        surface.set_at((px, py), color)


def point_in_polygon(x, y, polygon):
    """Check if point is inside polygon using ray casting"""
    if len(polygon) < 3:
        return False
    
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def draw_panel(screen, font, small_font, mode, vertices, fill_result):
    """Draw the control panel"""
    panel_x = DRAW_AREA[0]
    pygame.draw.rect(screen, PANEL_COLOR, (panel_x, 0, PANEL_AREA[0], PANEL_AREA[1]))
    
    # Title
    title = font.render("Polygon Fill Algorithms", True, TEXT_COLOR)
    screen.blit(title, (panel_x + 20, 20))
    
    subtitle = small_font.render("Interactive Fill Algorithms", True, ACCENT_COLOR)
    screen.blit(subtitle, (panel_x + 20, 55))
    
    # Instructions
    y = 100
    instructions = [
        "Controls:",
        "Click to add vertices (yellow)",
        "Right-click to complete",
        "",
        "1 - Scanline Fill (Green)",
        "2 - Flood Fill 4-conn (Blue)",
        "3 - Flood Fill 8-conn (Magenta)",
        "4 - Boundary Fill (Orange)",
        "",
        "C - Clear all",
        "ESC - Clear vertices only",
        "",
        f"Mode: {mode}",
        f"Vertices: {len(vertices)}"
    ]
    
    for line in instructions:
        txt = small_font.render(line, True, TEXT_COLOR)
        screen.blit(txt, (panel_x + 20, y))
        y += 25
    
    # Fill result
    if fill_result:
        algo, pixels, duration = fill_result
        y += 20
        screen.blit(font.render("Last Fill:", True, ACCENT_COLOR), (panel_x + 20, y))
        y += 35
        
        # Color-code the algorithm name
        algo_color = TEXT_COLOR
        if "Scanline" in algo:
            algo_color = SCANLINE_COLOR
        elif "4-connected" in algo:
            algo_color = FLOOD4_COLOR
        elif "8-connected" in algo:
            algo_color = FLOOD8_COLOR
        elif "Boundary" in algo:
            algo_color = BOUNDARY_FILL_COLOR
        
        screen.blit(small_font.render(algo, True, algo_color), (panel_x + 20, y))
        y += 25
        screen.blit(small_font.render(f"Pixels: {pixels}", True, TEXT_COLOR), (panel_x + 20, y))
        y += 25
        screen.blit(small_font.render(f"Time: {duration:.5f} s", True, TEXT_COLOR), (panel_x + 20, y))
        y += 25
        if pixels > 0:
            screen.blit(small_font.render(f"({duration/pixels*1e6:.3f} µs/pixel)", True, TEXT_COLOR), (panel_x + 20, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Polygon Fill Algorithms Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24, bold=True)
    small_font = pygame.font.SysFont("consolas", 18)
    
    draw_surface = pygame.Surface(DRAW_AREA)
    draw_surface.fill(BG_COLOR)
    
    vertices = []
    polygon_closed = False
    mode = "Drawing"
    fill_result = None
    running = True
    
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                
                if ev.button == 1 and mx < DRAW_AREA[0]:  # Left click
                    if not polygon_closed:
                        vertices.append((mx, my))
                        # Draw vertex
                        pygame.draw.circle(draw_surface, VERTEX_COLOR, (mx, my), 4)
                        # Draw edge from previous vertex with thickness
                        if len(vertices) > 1:
                            x1, y1 = vertices[-2]
                            x2, y2 = vertices[-1]
                            draw_line_bresenham(draw_surface, x1, y1, x2, y2, POLYGON_COLOR)
                            # Add thickness to prevent gaps
                            for dx in range(-2, 3):
                                for dy in range(-2, 3):
                                    if dx*dx + dy*dy <= 4:
                                        draw_line_bresenham(draw_surface, x1+dx, y1+dy, x2+dx, y2+dy, POLYGON_COLOR)
                
                elif ev.button == 3 and mx < DRAW_AREA[0]:  # Right click
                    if len(vertices) >= 3 and not polygon_closed:
                        # Close polygon with thick lines to prevent gaps
                        draw_polygon(draw_surface, vertices, POLYGON_COLOR)
                        polygon_closed = True
                        mode = "Ready to Fill"
            
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    draw_surface.fill(BG_COLOR)
                    vertices = []
                    polygon_closed = False
                    mode = "Drawing"
                    fill_result = None
                
                elif ev.key == pygame.K_ESCAPE:
                    draw_surface.fill(BG_COLOR)
                    vertices = []
                    polygon_closed = False
                    mode = "Drawing"
                    fill_result = None
                
                elif ev.key == pygame.K_1 and polygon_closed:
                    # Scanline Fill
                    draw_surface.fill(BG_COLOR)
                    t0 = time.perf_counter()
                    pixels = scanline_fill(draw_surface, vertices, SCANLINE_COLOR)
                    duration = time.perf_counter() - t0
                    draw_polygon(draw_surface, vertices, POLYGON_COLOR)
                    for v in vertices:
                        pygame.draw.circle(draw_surface, VERTEX_COLOR, v, 4)
                    mode = "Scanline Fill (Green)"
                    fill_result = ("Scanline Fill", pixels, duration)
                
                elif ev.key == pygame.K_2 and polygon_closed:
                    # Flood Fill 4-connected
                    draw_surface.fill(BG_COLOR)
                    draw_polygon(draw_surface, vertices, POLYGON_COLOR)
                    # Find a point inside polygon
                    cx = sum(v[0] for v in vertices) // len(vertices)
                    cy = sum(v[1] for v in vertices) // len(vertices)
                    t0 = time.perf_counter()
                    pixels = flood_fill_4(draw_surface, cx, cy, FLOOD4_COLOR, BG_COLOR)
                    duration = time.perf_counter() - t0
                    draw_polygon(draw_surface, vertices, POLYGON_COLOR)
                    for v in vertices:
                        pygame.draw.circle(draw_surface, VERTEX_COLOR, v, 4)
                    mode = "Flood Fill 4-conn (Blue)"
                    fill_result = ("Flood Fill 4-connected", pixels, duration)
                
                elif ev.key == pygame.K_3 and polygon_closed:
                    # Flood Fill 8-connected
                    draw_surface.fill(BG_COLOR)
                    draw_polygon(draw_surface, vertices, POLYGON_COLOR)
                    cx = sum(v[0] for v in vertices) // len(vertices)
                    cy = sum(v[1] for v in vertices) // len(vertices)
                    t0 = time.perf_counter()
                    pixels = flood_fill_8(draw_surface, cx, cy, FLOOD8_COLOR, BG_COLOR)
                    duration = time.perf_counter() - t0
                    draw_polygon(draw_surface, vertices, POLYGON_COLOR)
                    for v in vertices:
                        pygame.draw.circle(draw_surface, VERTEX_COLOR, v, 4)
                    mode = "Flood Fill 8-conn (Magenta)"
                    fill_result = ("Flood Fill 8-connected", pixels, duration)
                
                elif ev.key == pygame.K_4 and polygon_closed:
                    # Boundary Fill
                    draw_surface.fill(BG_COLOR)
                    draw_polygon(draw_surface, vertices, BOUNDARY_OUTLINE)
                    cx = sum(v[0] for v in vertices) // len(vertices)
                    cy = sum(v[1] for v in vertices) // len(vertices)
                    t0 = time.perf_counter()
                    pixels = boundary_fill(draw_surface, cx, cy, BOUNDARY_FILL_COLOR, BOUNDARY_OUTLINE)
                    duration = time.perf_counter() - t0
                    draw_polygon(draw_surface, vertices, BOUNDARY_OUTLINE)
                    for v in vertices:
                        pygame.draw.circle(draw_surface, VERTEX_COLOR, v, 4)
                    mode = "Boundary Fill (Orange)"
                    fill_result = ("Boundary Fill", pixels, duration)
        
        screen.blit(draw_surface, (0, 0))
        draw_panel(screen, font, small_font, mode, vertices, fill_result)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()