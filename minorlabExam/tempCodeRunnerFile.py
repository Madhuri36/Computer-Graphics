import pygame
import math
import numpy as np
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
CYAN = (100, 255, 255)
MAGENTA = (255, 100, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

class Point3D:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def to_array(self):
        return np.array([self.x, self.y, self.z, 1.0])
    
    @classmethod
    def from_array(cls, arr):
        return cls(arr[0], arr[1], arr[2])

class LineDrawingAlgorithms:
    @staticmethod
    def dda_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Digital Differential Analyzer line drawing algorithm"""
        points = []
        dx = x2 - x1
        dy = y2 - y1
        
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return [(x1, y1)]
        
        x_inc = dx / steps
        y_inc = dy / steps
        
        x, y = x1, y1
        for _ in range(int(steps) + 1):
            points.append((int(round(x)), int(round(y))))
            x += x_inc
            y += y_inc
        
        return points
    
    @staticmethod
    def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Bresenham's line drawing algorithm"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx - dy
        x, y = x1, y1
        
        while True:
            points.append((x, y))
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points

class Transform3D:
    @staticmethod
    def translation_matrix(tx: float, ty: float, tz: float):
        return np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_x_matrix(angle: float):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return np.array([
            [1, 0, 0, 0],
            [0, cos_a, -sin_a, 0],
            [0, sin_a, cos_a, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_y_matrix(angle: float):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return np.array([
            [cos_a, 0, sin_a, 0],
            [0, 1, 0, 0],
            [-sin_a, 0, cos_a, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_z_matrix(angle: float):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return np.array([
            [cos_a, -sin_a, 0, 0],
            [sin_a, cos_a, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def scaling_matrix(sx: float, sy: float, sz: float):
        return np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ])

class Projection:
    @staticmethod
    def orthographic(point: Point3D, center_x: int, center_y: int, scale: float = 1.0):
        x = center_x + point.x * scale
        y = center_y - point.y * scale  # Flip Y for screen coordinates
        return (int(x), int(y))
    
    @staticmethod
    def perspective(point: Point3D, center_x: int, center_y: int, focal_length: float = 400, scale: float = 1.0):
        # Move camera back to create proper perspective
        z = point.z + focal_length
        if z <= 0.1:
            z = 0.1  # Avoid division by zero
        
        x = center_x + (point.x * focal_length * scale) / z
        y = center_y - (point.y * focal_length * scale) / z
        return (int(x), int(y))

class Object3D:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.color = WHITE
        self.original_vertices = []
    
    def add_vertex(self, point: Point3D):
        self.vertices.append(point)
        self.original_vertices.append(Point3D(point.x, point.y, point.z))
    
    def add_edge(self, v1_idx: int, v2_idx: int):
        if 0 <= v1_idx < len(self.vertices) and 0 <= v2_idx < len(self.vertices):
            self.edges.append((v1_idx, v2_idx))
    
    def clear(self):
        self.vertices.clear()
        self.edges.clear()
        self.original_vertices.clear()
    
    def apply_transformation(self, matrix):
        for i, vertex in enumerate(self.original_vertices):
            transformed = matrix @ vertex.to_array()
            self.vertices[i] = Point3D.from_array(transformed)
    
    def reset_transformations(self):
        for i, original in enumerate(self.original_vertices):
            self.vertices[i] = Point3D(original.x, original.y, original.z)
    
    def create_cube(self, size: float = 100):
        """Create a cube centered at origin"""
        self.clear()
        s = size / 2
        
        # Define 8 vertices of cube
        vertices = [
            Point3D(-s, -s, -s), Point3D(s, -s, -s), Point3D(s, s, -s), Point3D(-s, s, -s),  # Front face
            Point3D(-s, -s, s), Point3D(s, -s, s), Point3D(s, s, s), Point3D(-s, s, s)      # Back face
        ]
        
        for vertex in vertices:
            self.add_vertex(vertex)
        
        # Define 12 edges
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Front face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Back face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]
        
        for edge in edges:
            self.add_edge(*edge)
    
    def create_pyramid(self, size: float = 100):
        """Create a pyramid"""
        self.clear()
        s = size / 2
        h = size
        
        vertices = [
            Point3D(-s, -s, -s), Point3D(s, -s, -s), Point3D(s, -s, s), Point3D(-s, -s, s),  # Base
            Point3D(0, h, 0)  # Apex
        ]
        
        for vertex in vertices:
            self.add_vertex(vertex)
        
        # Base edges
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        # Edges to apex
        edges.extend([(0, 4), (1, 4), (2, 4), (3, 4)])
        
        for edge in edges:
            self.add_edge(*edge)

class Graphics3DProgram:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("3D Graphics Program - Line Algorithms & Transformations")
        self.clock = pygame.time.Clock()
        
        # Drawing state
        self.drawing_mode = True
        self.drawing_points = []
        self.temp_point = None
        
        # 3D Object
        self.object3d = Object3D()
        
        # Transformation parameters
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
        
        # Projection settings
        self.projection_mode = "orthographic"  # "orthographic" or "perspective"
        self.line_algorithm = "dda"  # "dda" or "bresenham"
        
        # View settings
        self.viewport_x = SCREEN_WIDTH // 3
        self.viewport_y = SCREEN_HEIGHT // 2
        self.scale = 1.8
        
        # Font for UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Auto rotation
        self.auto_rotate = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keypress(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_click(event.pos)
        
        return True
    
    def handle_keypress(self, key):
        # Mode switches
        if key == pygame.K_m:
            self.drawing_mode = not self.drawing_mode
        elif key == pygame.K_p:
            self.projection_mode = "perspective" if self.projection_mode == "orthographic" else "orthographic"
        elif key == pygame.K_l:
            self.line_algorithm = "bresenham" if self.line_algorithm == "dda" else "dda"
        elif key == pygame.K_r:
            self.auto_rotate = not self.auto_rotate
        
        # Preset objects
        elif key == pygame.K_c:
            self.object3d.create_cube(150)
        elif key == pygame.K_t:
            self.object3d.create_pyramid(150)
        elif key == pygame.K_DELETE:
            self.object3d.clear()
            self.drawing_points.clear()
        
        # Transformations
        elif key == pygame.K_x:
            self.rotation_x += 0.1
        elif key == pygame.K_y:
            self.rotation_y += 0.1
        elif key == pygame.K_z:
            self.rotation_z += 0.1
        elif key == pygame.K_LEFT:
            self.translation_x -= 10
        elif key == pygame.K_RIGHT:
            self.translation_x += 10
        elif key == pygame.K_UP:
            self.translation_y += 10
        elif key == pygame.K_DOWN:
            self.translation_y -= 10
        elif key == pygame.K_PAGEUP:
            self.translation_z += 10
        elif key == pygame.K_PAGEDOWN:
            self.translation_z -= 10
        elif key == pygame.K_EQUALS:
            self.scale_x = self.scale_y = self.scale_z = min(3.0, self.scale_x + 0.1)
        elif key == pygame.K_MINUS:
            self.scale_x = self.scale_y = self.scale_z = max(0.1, self.scale_x - 0.1)
        
        # Reset
        elif key == pygame.K_SPACE:
            self.reset_transformations()
    
    def handle_mouse_click(self, pos):
        if self.drawing_mode:
            # Convert screen coordinates to 3D coordinates
            x = (pos[0] - self.viewport_x) / self.scale
            y = (self.viewport_y - pos[1]) / self.scale
            z = 0  # Default Z for new points
            
            point3d = Point3D(x, y, z)
            
            if len(self.drawing_points) == 0:
                # First point
                self.drawing_points.append(len(self.object3d.vertices))
                self.object3d.add_vertex(point3d)
            else:
                # Add point and connect to previous
                prev_idx = self.drawing_points[-1]
                new_idx = len(self.object3d.vertices)
                self.object3d.add_vertex(point3d)
                self.object3d.add_edge(prev_idx, new_idx)
                self.drawing_points.append(new_idx)
    
    def reset_transformations(self):
        self.rotation_x = self.rotation_y = self.rotation_z = 0
        self.translation_x = self.translation_y = self.translation_z = 0
        self.scale_x = self.scale_y = self.scale_z = 1.0
    
    def update_transformations(self):
        if self.auto_rotate:
            self.rotation_x += 0.01
            self.rotation_y += 0.015
            self.rotation_z += 0.008
        
        # Create transformation matrix
        translation = Transform3D.translation_matrix(self.translation_x, self.translation_y, self.translation_z)
        rotation_x = Transform3D.rotation_x_matrix(self.rotation_x)
        rotation_y = Transform3D.rotation_y_matrix(self.rotation_y)
        rotation_z = Transform3D.rotation_z_matrix(self.rotation_z)
        scaling = Transform3D.scaling_matrix(self.scale_x, self.scale_y, self.scale_z)
        
        # Combine transformations: Scale -> Rotate -> Translate
        transform_matrix = translation @ rotation_z @ rotation_y @ rotation_x @ scaling
        
        # Apply transformations
        self.object3d.apply_transformation(transform_matrix)
    
    def draw_line_with_algorithm(self, surface, start, end, color):
        """Draw line using selected algorithm"""
        if self.line_algorithm == "dda":
            points = LineDrawingAlgorithms.dda_line(start[0], start[1], end[0], end[1])
        else:
            points = LineDrawingAlgorithms.bresenham_line(start[0], start[1], end[0], end[1])
        
        for point in points:
            if 0 <= point[0] < SCREEN_WIDTH and 0 <= point[1] < SCREEN_HEIGHT:
                surface.set_at(point, color)
    
    def render_object(self):
        """Render the 3D object"""
        # Draw edges
        for edge_idx, (v1_idx, v2_idx) in enumerate(self.object3d.edges):
            if v1_idx < len(self.object3d.vertices) and v2_idx < len(self.object3d.vertices):
                v1 = self.object3d.vertices[v1_idx]
                v2 = self.object3d.vertices[v2_idx]
                
                # Project to 2D
                if self.projection_mode == "orthographic":
                    p1 = Projection.orthographic(v1, self.viewport_x, self.viewport_y, self.scale)
                    p2 = Projection.orthographic(v2, self.viewport_x, self.viewport_y, self.scale)
                else:
                    p1 = Projection.perspective(v1, self.viewport_x, self.viewport_y, 400, self.scale)
                    p2 = Projection.perspective(v2, self.viewport_x, self.viewport_y, 400, self.scale)
                
                # Color coding for edges
                colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]
                edge_color = colors[edge_idx % len(colors)]
                
                # Draw line using selected algorithm
                self.draw_line_with_algorithm(self.screen, p1, p2, edge_color)
        
        # Draw vertices
        for i, vertex in enumerate(self.object3d.vertices):
            if self.projection_mode == "orthographic":
                point = Projection.orthographic(vertex, self.viewport_x, self.viewport_y, self.scale)
            else:
                point = Projection.perspective(vertex, self.viewport_x, self.viewport_y, 400, self.scale)
            
            pygame.draw.circle(self.screen, WHITE, point, 4)
            # Draw vertex number
            text = self.small_font.render(str(i), True, WHITE)
            self.screen.blit(text, (point[0] + 6, point[1] - 10))
    
    def draw_ui(self):
        """Draw user interface"""
        y_offset = 10
        line_height = 25
        
        # Title
        title = self.font.render("3D Graphics Program", True, WHITE)
        self.screen.blit(title, (10, y_offset))
        y_offset += line_height * 1.5
        
        # Current settings
        settings = [
            f"Mode: {'Drawing' if self.drawing_mode else 'Transform'} (M)",
            f"Projection: {self.projection_mode.title()} (P)",
            f"Line Algorithm: {self.line_algorithm.upper()} (L)",
            f"Auto Rotate: {'ON' if self.auto_rotate else 'OFF'} (R)",
            "",
            "Transformations:",
            f"Rotation X: {self.rotation_x:.2f} (X)",
            f"Rotation Y: {self.rotation_y:.2f} (Y)", 
            f"Rotation Z: {self.rotation_z:.2f} (Z)",
            f"Translation: ({self.translation_x:.0f}, {self.translation_y:.0f}, {self.translation_z:.0f})",
            f"Scale: {self.scale_x:.2f}",
            "",
            "Controls:",
            "Click: Add point/edge",
            "C: Create cube",
            "T: Create pyramid", 
            "DEL: Clear object",
            "Arrows: Translate X/Y",
            "PgUp/PgDn: Translate Z",
            "+/-: Scale",
            "SPACE: Reset transforms"
        ]
        
        for setting in settings:
            if setting:
                color = YELLOW if setting.startswith(("Mode:", "Projection:", "Line Algorithm:")) else WHITE
                text = self.small_font.render(setting, True, color)
                self.screen.blit(text, (10, y_offset))
            y_offset += 20
        
        # Draw coordinate system
        center = (self.viewport_x, self.viewport_y)
        axis_length = 50
        
        # X axis (red)
        pygame.draw.line(self.screen, RED, center, (center[0] + axis_length, center[1]), 2)
        pygame.draw.polygon(self.screen, RED, [(center[0] + axis_length, center[1]), 
                                              (center[0] + axis_length - 10, center[1] - 5),
                                              (center[0] + axis_length - 10, center[1] + 5)])
        
        # Y axis (green) 
        pygame.draw.line(self.screen, GREEN, center, (center[0], center[1] - axis_length), 2)
        pygame.draw.polygon(self.screen, GREEN, [(center[0], center[1] - axis_length),
                                                (center[0] - 5, center[1] - axis_length + 10),
                                                (center[0] + 5, center[1] - axis_length + 10)])
        
        # Z axis (blue) - diagonal to show depth
        z_end = (center[0] - 35, center[1] - 35)
        pygame.draw.line(self.screen, BLUE, center, z_end, 2)
        pygame.draw.polygon(self.screen, BLUE, [z_end, (z_end[0] + 8, z_end[1] + 3),
                                               (z_end[0] + 3, z_end[1] + 8)])
        
        # Axis labels
        x_label = self.small_font.render("X", True, RED)
        y_label = self.small_font.render("Y", True, GREEN)
        z_label = self.small_font.render("Z", True, BLUE)
        self.screen.blit(x_label, (center[0] + axis_length + 10, center[1] - 10))
        self.screen.blit(y_label, (center[0] + 5, center[1] - axis_length - 15))
        self.screen.blit(z_label, (z_end[0] - 15, z_end[1] - 15))
        
        # Status
        status = f"Vertices: {len(self.object3d.vertices)} | Edges: {len(self.object3d.edges)}"
        status_text = self.small_font.render(status, True, LIGHT_GRAY)
        self.screen.blit(status_text, (10, SCREEN_HEIGHT - 30))
    
    def run(self):
        """Main game loop"""
        running = True
        
        # Create a default cube to start with
        self.object3d.create_cube(120)
        
        while running:
            running = self.handle_events()
            
            # Update
            self.update_transformations()
            
            # Render
            self.screen.fill(BLACK)
            self.render_object()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    program = Graphics3DProgram()
    program.run()