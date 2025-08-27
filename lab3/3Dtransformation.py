import pygame
import numpy as np
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
GRID_SIZE = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (64, 64, 64)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
CYAN = (100, 255, 255)
MAGENTA = (255, 100, 255)

class Object3D:
    def __init__(self, vertices, edges, color, name):
        self.original_vertices = np.array(vertices)
        self.vertices = np.array(vertices)
        self.edges = edges
        self.color = color
        self.name = name
        self.transform_matrix = np.eye(4)  # 4x4 identity matrix for homogeneous coordinates
        
        # Calculate center of the object for proper rotation
        self.center = np.mean(self.original_vertices, axis=0)
    
    def apply_transformation(self, matrix, rotate_around_center=False):
        """Apply transformation matrix to the current transformation"""
        if rotate_around_center:
            # Calculate the CURRENT center of the transformed object
            current_center = np.mean(self.vertices, axis=0)
            
            # For rotations/scaling, translate to origin, transform, then translate back
            translate_to_origin = Transform3D.translation(-current_center[0], -current_center[1], -current_center[2])
            translate_back = Transform3D.translation(current_center[0], current_center[1], current_center[2])
            
            # Apply transformation around current center
            transformation_matrix = np.dot(translate_back, np.dot(matrix, translate_to_origin))
            self.transform_matrix = np.dot(transformation_matrix, self.transform_matrix)
        else:
            self.transform_matrix = np.dot(matrix, self.transform_matrix)
        
        # Apply the cumulative transformation to original vertices
        homogeneous_vertices = np.column_stack([self.original_vertices, np.ones(len(self.original_vertices))])
        transformed = np.dot(homogeneous_vertices, self.transform_matrix.T)
        self.vertices = transformed[:, :3]  # Extract x, y, z coordinates
    
    def reset_transformation(self):
        """Reset to original state"""
        self.transform_matrix = np.eye(4)
        self.vertices = self.original_vertices.copy()
        self.center = np.mean(self.original_vertices, axis=0)

class Transform3D:
    @staticmethod
    def translation(dx, dy, dz):
        """Create translation matrix"""
        matrix = np.eye(4)
        matrix[0, 3] = dx
        matrix[1, 3] = dy
        matrix[2, 3] = dz
        return matrix
    
    @staticmethod
    def scaling(sx, sy, sz):
        """Create scaling matrix"""
        matrix = np.eye(4)
        matrix[0, 0] = sx
        matrix[1, 1] = sy
        matrix[2, 2] = sz
        return matrix
    
    @staticmethod
    def rotation_x(angle):
        """Create rotation matrix around X-axis"""
        matrix = np.eye(4)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        matrix[1, 1] = cos_a
        matrix[1, 2] = -sin_a
        matrix[2, 1] = sin_a
        matrix[2, 2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_y(angle):
        """Create rotation matrix around Y-axis"""
        matrix = np.eye(4)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        matrix[0, 0] = cos_a
        matrix[0, 2] = sin_a
        matrix[2, 0] = -sin_a
        matrix[2, 2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_z(angle):
        """Create rotation matrix around Z-axis"""
        matrix = np.eye(4)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        matrix[0, 0] = cos_a
        matrix[0, 1] = -sin_a
        matrix[1, 0] = sin_a
        matrix[1, 1] = cos_a
        return matrix
    
    @staticmethod
    def reflection_xy():
        """Reflect across XY plane (Z = 0)"""
        matrix = np.eye(4)
        matrix[2, 2] = -1
        return matrix
    
    @staticmethod
    def reflection_xz():
        """Reflect across XZ plane (Y = 0)"""
        matrix = np.eye(4)
        matrix[1, 1] = -1
        return matrix
    
    @staticmethod
    def reflection_yz():
        """Reflect across YZ plane (X = 0)"""
        matrix = np.eye(4)
        matrix[0, 0] = -1
        return matrix
    
    @staticmethod
    def shearing_xy(shx, shy):
        """Shearing in XY plane"""
        matrix = np.eye(4)
        matrix[0, 1] = shx
        matrix[1, 0] = shy
        return matrix
    
    @staticmethod
    def shearing_xz(shx, shz):
        """Shearing in XZ plane"""
        matrix = np.eye(4)
        matrix[0, 2] = shx
        matrix[2, 0] = shz
        return matrix
    
    @staticmethod
    def shearing_yz(shy, shz):
        """Shearing in YZ plane"""
        matrix = np.eye(4)
        matrix[1, 2] = shy
        matrix[2, 1] = shz
        return matrix

class Renderer3D:
    def __init__(self, screen):
        self.screen = screen
        self.camera_distance = 500
        self.screen_center = (WIDTH // 2, HEIGHT // 2)
    
    def project_3d_to_2d(self, vertex):
        """Project 3D vertex to 2D screen coordinates using perspective projection"""
        x, y, z = vertex
        # Simple perspective projection
        if z + self.camera_distance != 0:
            screen_x = int(x * self.camera_distance / (z + self.camera_distance) + self.screen_center[0])
            screen_y = int(-y * self.camera_distance / (z + self.camera_distance) + self.screen_center[1])
        else:
            screen_x = int(x + self.screen_center[0])
            screen_y = int(-y + self.screen_center[1])
        return (screen_x, screen_y)
    
    def draw_grid(self):
        """Draw background grid"""
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y), 1)
    
    def draw_object(self, obj):
        """Draw 3D object"""
        projected_vertices = []
        for vertex in obj.vertices:
            projected_vertices.append(self.project_3d_to_2d(vertex))
        
        # Draw edges
        for edge in obj.edges:
            start_pos = projected_vertices[edge[0]]
            end_pos = projected_vertices[edge[1]]
            pygame.draw.line(self.screen, obj.color, start_pos, end_pos, 2)
        
        # Draw vertices
        for pos in projected_vertices:
            pygame.draw.circle(self.screen, WHITE, pos, 3)

def create_cube(size=50):
    """Create a cube object"""
    s = size
    vertices = [
        [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # Back face
        [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]       # Front face
    ]
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # Back face
        [4, 5], [5, 6], [6, 7], [7, 4],  # Front face
        [0, 4], [1, 5], [2, 6], [3, 7]   # Connecting edges
    ]
    return Object3D(vertices, edges, RED, "Cube")

def create_tetrahedron(size=60):
    """Create a tetrahedron object"""
    s = size
    vertices = [
        [0, s, 0],
        [-s, -s/2, s/2],
        [s, -s/2, s/2],
        [0, -s/2, -s]
    ]
    edges = [
        [0, 1], [0, 2], [0, 3],
        [1, 2], [1, 3], [2, 3]
    ]
    return Object3D(vertices, edges, GREEN, "Tetrahedron")

def create_octahedron(size=50):
    """Create an octahedron object"""
    s = size
    vertices = [
        [0, s, 0],    # Top
        [0, -s, 0],   # Bottom
        [s, 0, 0],    # Right
        [-s, 0, 0],   # Left
        [0, 0, s],    # Front
        [0, 0, -s]    # Back
    ]
    edges = [
        [0, 2], [0, 3], [0, 4], [0, 5],  # Top to others
        [1, 2], [1, 3], [1, 4], [1, 5],  # Bottom to others
        [2, 4], [2, 5], [3, 4], [3, 5]   # Middle connections
    ]
    return Object3D(vertices, edges, BLUE, "Octahedron")

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Hybrid Transformations with Homogeneous Coordinates")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Create objects
    objects = [
        create_cube(),
        create_tetrahedron()
    ]
    
    current_object_index = 0
    renderer = Renderer3D(screen)
    
    # Transformation modes
    modes = ["NONE", "TRANSLATION", "SCALING", "ROTATION", "REFLECTION", "SHEARING"]
    current_mode = 0
    
    # Transformation parameters
    transform_speed = 2.0
    rotation_speed = 0.03
    scale_speed = 0.02
    shear_speed = 0.01
    
    # Reflection states
    reflection_planes = ["XY", "XZ", "YZ"]
    current_reflection_plane = 0
    
    # Shearing states
    shear_planes = ["XY", "XZ", "YZ"]
    current_shear_plane = 0
    
    running = True
    keys_pressed = set()
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                keys_pressed.add(event.key)
                
                if event.key == pygame.K_1:
                    current_object_index = 0  # Cube
                elif event.key == pygame.K_2:
                    current_object_index = 1  # Tetrahedron
                
                elif event.key == pygame.K_t:
                    current_mode = 1  # Translation
                elif event.key == pygame.K_s:
                    current_mode = 2  # Scaling
                elif event.key == pygame.K_r:
                    current_mode = 3  # Rotation
                elif event.key == pygame.K_f:
                    current_mode = 4  # Reflection
                elif event.key == pygame.K_h:
                    current_mode = 5  # Shearing
                
                elif event.key == pygame.K_SPACE:
                    objects[current_object_index].reset_transformation()
            
            elif event.type == pygame.KEYUP:
                keys_pressed.discard(event.key)
        
        current_obj = objects[current_object_index]
        
        # Handle continuous key presses for transformations ONLY when in specific modes
        if current_mode == 1:  # Translation
            dx = dy = dz = 0
            if pygame.K_LEFT in keys_pressed:
                dx = -transform_speed
            if pygame.K_RIGHT in keys_pressed:
                dx = transform_speed
            if pygame.K_UP in keys_pressed:
                dy = transform_speed
            if pygame.K_DOWN in keys_pressed:
                dy = -transform_speed
            if pygame.K_q in keys_pressed:
                dz = -transform_speed
            if pygame.K_e in keys_pressed:
                dz = transform_speed
            
            if dx != 0 or dy != 0 or dz != 0:
                matrix = Transform3D.translation(dx, dy, dz)
                current_obj.apply_transformation(matrix, rotate_around_center=False)
        
        elif current_mode == 2:  # Scaling
            sx = sy = sz = 1.0
            if pygame.K_LEFT in keys_pressed:
                sx = 1 - scale_speed
            if pygame.K_RIGHT in keys_pressed:
                sx = 1 + scale_speed
            if pygame.K_UP in keys_pressed:
                sy = 1 + scale_speed
            if pygame.K_DOWN in keys_pressed:
                sy = 1 - scale_speed
            if pygame.K_q in keys_pressed:
                sz = 1 - scale_speed
            if pygame.K_e in keys_pressed:
                sz = 1 + scale_speed
            
            if sx != 1.0 or sy != 1.0 or sz != 1.0:
                matrix = Transform3D.scaling(sx, sy, sz)
                current_obj.apply_transformation(matrix, rotate_around_center=True)
        
        elif current_mode == 3:  # Rotation - ONLY when explicitly in rotation mode
            rx = ry = rz = 0
            if pygame.K_LEFT in keys_pressed:
                ry = -rotation_speed
            if pygame.K_RIGHT in keys_pressed:
                ry = rotation_speed
            if pygame.K_UP in keys_pressed:
                rx = -rotation_speed
            if pygame.K_DOWN in keys_pressed:
                rx = rotation_speed
            if pygame.K_q in keys_pressed:
                rz = -rotation_speed
            if pygame.K_e in keys_pressed:
                rz = rotation_speed
            
            # Apply rotations only when keys are pressed and we're in rotation mode
            if rx != 0:
                matrix = Transform3D.rotation_x(rx)
                current_obj.apply_transformation(matrix, rotate_around_center=True)
            if ry != 0:
                matrix = Transform3D.rotation_y(ry)
                current_obj.apply_transformation(matrix, rotate_around_center=True)
            if rz != 0:
                matrix = Transform3D.rotation_z(rz)
                current_obj.apply_transformation(matrix, rotate_around_center=True)
        
        elif current_mode == 4:  # Reflection
            if pygame.K_LEFT in keys_pressed or pygame.K_RIGHT in keys_pressed:
                current_reflection_plane = (current_reflection_plane + 1) % 3
                if reflection_planes[current_reflection_plane] == "XY":
                    matrix = Transform3D.reflection_xy()
                elif reflection_planes[current_reflection_plane] == "XZ":
                    matrix = Transform3D.reflection_xz()
                elif reflection_planes[current_reflection_plane] == "YZ":
                    matrix = Transform3D.reflection_yz()
                current_obj.apply_transformation(matrix, rotate_around_center=False)
                pygame.time.wait(200)  # Prevent rapid reflections
        
        elif current_mode == 5:  # Shearing
            if pygame.K_LEFT in keys_pressed or pygame.K_RIGHT in keys_pressed:
                current_shear_plane = (current_shear_plane + 1) % 3
                pygame.time.wait(200)  # Prevent rapid changes
            
            shx = shy = shz = 0
            if pygame.K_UP in keys_pressed:
                if shear_planes[current_shear_plane] == "XY":
                    shx = shear_speed
                elif shear_planes[current_shear_plane] == "XZ":
                    shx = shear_speed
                elif shear_planes[current_shear_plane] == "YZ":
                    shy = shear_speed
            if pygame.K_DOWN in keys_pressed:
                if shear_planes[current_shear_plane] == "XY":
                    shx = -shear_speed
                elif shear_planes[current_shear_plane] == "XZ":
                    shx = -shear_speed
                elif shear_planes[current_shear_plane] == "YZ":
                    shy = -shear_speed
            
            if shx != 0 or shy != 0 or shz != 0:
                if shear_planes[current_shear_plane] == "XY":
                    matrix = Transform3D.shearing_xy(shx, shy)
                elif shear_planes[current_shear_plane] == "XZ":
                    matrix = Transform3D.shearing_xz(shx, shz)
                elif shear_planes[current_shear_plane] == "YZ":
                    matrix = Transform3D.shearing_yz(shy, shz)
                current_obj.apply_transformation(matrix, rotate_around_center=False)
        
        # Clear screen and draw
        screen.fill(BLACK)
        renderer.draw_grid()
        
        # Draw all objects with current one highlighted
        for i, obj in enumerate(objects):
            if i == current_object_index:
                renderer.draw_object(obj)
        
        # Draw UI
        y_offset = 10
        ui_texts = [
            "Controls:",
            "--------------------",
            "1 - Select Cube",
            "2 - Select Tetrahedron",
            "T - Translation Mode",
            "S - Scaling Mode", 
            "R - Rotation Mode",
            "F - Reflection Mode",
            "H - Shearing Mode",
            "Arrow Keys - Transform",
            "Q/E - Z-axis transform",
            "SPACE - Reset",
            "",
            f"Current Object: {current_obj.name}",
            f"Current Mode: {modes[current_mode]}"
        ]
        
        if current_mode == 4:  # Reflection
            ui_texts.append(f"Reflection Plane: {reflection_planes[current_reflection_plane]}")
        elif current_mode == 5:  # Shearing
            ui_texts.append(f"Shear Plane: {shear_planes[current_shear_plane]}")
        
        for text in ui_texts:
            color = WHITE if not text.startswith("Current") else YELLOW
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()