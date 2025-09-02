import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
BACKGROUND = (20, 25, 30)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

class Vector3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Cube3D:
    def __init__(self, size=100):
        s = size / 2
        self.vertices = [
            Vector3D(-s, -s, -s), Vector3D(s, -s, -s), Vector3D(s, s, -s), Vector3D(-s, s, -s),
            Vector3D(-s, -s, s), Vector3D(s, -s, s), Vector3D(s, s, s), Vector3D(-s, s, s),
        ]
        
        # Define edges instead of faces for wireframe
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # back face
            (4, 5), (5, 6), (6, 7), (7, 4),  # front face
            (0, 4), (1, 5), (2, 6), (3, 7),  # connecting edges
        ]
        
        self.rotation = Vector3D(0, 0, 0)
    
    def rotate(self, rx, ry, rz):
        self.rotation.x += rx
        self.rotation.y += ry
        self.rotation.z += rz
    
    def get_transformed_vertices(self):
        transformed = []
        cos_x, sin_x = math.cos(self.rotation.x), math.sin(self.rotation.x)
        cos_y, sin_y = math.cos(self.rotation.y), math.sin(self.rotation.y)
        cos_z, sin_z = math.cos(self.rotation.z), math.sin(self.rotation.z)
        
        for vertex in self.vertices:
            x, y, z = vertex.x, vertex.y, vertex.z
            
            # X rotation
            y_new = y * cos_x - z * sin_x
            z_new = y * sin_x + z * cos_x
            y, z = y_new, z_new
            
            # Y rotation
            x_new = x * cos_y + z * sin_y
            z_new = -x * sin_y + z * cos_y
            x, z = x_new, z_new
            
            # Z rotation
            x_new = x * cos_z - y * sin_z
            y_new = x * sin_z + y * cos_z
            x, y = x_new, y_new
            
            transformed.append(Vector3D(x, y, z))
        
        return transformed

class ProjectionDemo:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("3D Wireframe Projections")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.cube = Cube3D(100)
        self.viewer_distance = 400
        self.cube_z_offset = 300
    
    def orthogonal_projection(self, point3d, center_x, center_y):
        return (center_x + point3d.x, center_y - point3d.y)
    
    def perspective_projection(self, point3d, center_x, center_y):
        z = point3d.z + self.cube_z_offset
        if z <= 1:
            z = 1
        
        factor = self.viewer_distance / z
        x = center_x + point3d.x * factor
        y = center_y - point3d.y * factor
        
        return (x, y)
    
    def draw_cube(self, vertices_3d, center_x, center_y, projection_type, title):
        # Project vertices
        if projection_type == "orthogonal":
            vertices_2d = [self.orthogonal_projection(v, center_x, center_y) for v in vertices_3d]
        else:
            vertices_2d = [self.perspective_projection(v, center_x, center_y) for v in vertices_3d]
        
        # Draw wireframe edges
        for edge in self.cube.edges:
            start_pos = vertices_2d[edge[0]]
            end_pos = vertices_2d[edge[1]]
            pygame.draw.line(self.screen, WHITE, start_pos, end_pos, 1)
        
        # Draw vertices as red dots
        for vertex_2d in vertices_2d:
            pygame.draw.circle(self.screen, RED, (int(vertex_2d[0]), int(vertex_2d[1])), 4)
        
        # Draw title
        title_surface = self.font.render(title, True, WHITE)
        title_rect = title_surface.get_rect(centerx=center_x, y=30)
        self.screen.blit(title_surface, title_rect)
        
        # Draw depth info
        depth_info = f"Z-offset: {self.cube_z_offset}"
        depth_surface = pygame.font.Font(None, 24).render(depth_info, True, YELLOW)
        depth_rect = depth_surface.get_rect(centerx=center_x, y=60)
        self.screen.blit(depth_surface, depth_rect)
    
    def draw_ui(self):
        pygame.draw.line(self.screen, GRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        
        instructions = [
            "Controls:",
            "Arrow keys - Manual rotation",
            "Z/X - Move cube closer/farther",
            "R - Reset cube position",
            "ESC - Exit"
        ]
        
        y_start = HEIGHT - 120
        for i, text in enumerate(instructions):
            color = YELLOW if i == 0 else WHITE
            surface = pygame.font.Font(None, 24).render(text, True, color)
            self.screen.blit(surface, (10, y_start + i * 22))
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.cube.rotation = Vector3D(0, 0, 0)
                        self.cube_z_offset = 300
                    elif event.key == pygame.K_z:
                        self.cube_z_offset = max(100, self.cube_z_offset - 20)
                    elif event.key == pygame.K_x:
                        self.cube_z_offset = min(500, self.cube_z_offset + 20)
            
            # Handle continuous input for manual rotation
            keys = pygame.key.get_pressed()
            rotation_speed = 0.02
            
            if keys[pygame.K_LEFT]:
                self.cube.rotate(0, -rotation_speed, 0)
            if keys[pygame.K_RIGHT]:
                self.cube.rotate(0, rotation_speed, 0)
            if keys[pygame.K_UP]:
                self.cube.rotate(-rotation_speed, 0, 0)
            if keys[pygame.K_DOWN]:
                self.cube.rotate(rotation_speed, 0, 0)
            
            # Clear and draw
            self.screen.fill(BACKGROUND)
            
            vertices_3d = self.cube.get_transformed_vertices()
            
            # Draw both projections side by side
            self.draw_cube(vertices_3d, WIDTH // 4, HEIGHT // 2, "orthogonal", "Orthogonal Projection")
            self.draw_cube(vertices_3d, 3 * WIDTH // 4, HEIGHT // 2, "perspective", "Perspective Projection")
            
            self.draw_ui()
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    demo = ProjectionDemo()
    demo.run()