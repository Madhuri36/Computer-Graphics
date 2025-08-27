import pygame
import numpy as np
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (17, 24, 39)      # Dark Blue-Gray
TEXT_COLOR = (243, 244, 246) # Light Gray
AXIS_COLOR = (75, 85, 99)    # Mid Gray
RED = (239, 68, 68)          # Bright Red
BLUE = (59, 130, 246)        # Bright Blue
SLIDER_BG = (55, 65, 81)
SLIDER_HANDLE = (209, 213, 219)


class Transform2D:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2D Transformations Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Original polygon
        self.sides = 6
        self.original_polygon = self.create_polygon(self.sides, 75)
        self.transformed_polygon = self.original_polygon.copy()
        
        # Transformation parameters
        self.tx, self.ty = 0, 0
        self.sx, self.sy = 1, 1
        self.angle = 0
        self.shx, self.shy = 0, 0
        self.reflect_x, self.reflect_y = False, False
        
        # Slider for controlling sides
        self.slider_rect = pygame.Rect(20, HEIGHT - 50, 200, 10)
        self.slider_pos = ((self.sides - 3) / 9) * self.slider_rect.width
    
    def create_polygon(self, sides, radius):
        points = []
        for i in range(sides):
            angle = 2 * math.pi * i / sides
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            points.append([x, y, 1])
        return np.array(points).T
    
    def translate(self, tx, ty):
        return np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]])
    
    def scale(self, sx, sy):
        return np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
    
    def rotate(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
    
    def shear(self, shx, shy):
        return np.array([[1, shx, 0], [shy, 1, 0], [0, 0, 1]])
    
    def reflect(self, reflect_x, reflect_y):
        rx = -1 if reflect_x else 1
        ry = -1 if reflect_y else 1
        return np.array([[rx, 0, 0], [0, ry, 0], [0, 0, 1]])
    
    def apply_transformations(self):
        transform_matrix = np.eye(3)
        transform_matrix = self.scale(self.sx, self.sy) @ transform_matrix
        transform_matrix = self.rotate(self.angle) @ transform_matrix
        transform_matrix = self.shear(self.shx, self.shy) @ transform_matrix
        transform_matrix = self.reflect(self.reflect_x, self.reflect_y) @ transform_matrix
        transformed_centered = transform_matrix @ self.original_polygon
        translation_matrix = self.translate(self.tx, self.ty)
        self.transformed_polygon = translation_matrix @ transformed_centered

    def world_to_screen(self, points):
        screen_points = []
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        for i in range(points.shape[1]):
            x = int(points[0, i] + center_x)
            y = int(-points[1, i] + center_y)
            screen_points.append([x, y])
        return screen_points
    
    def handle_slider(self, mouse_pos):
        if self.slider_rect.collidepoint(mouse_pos):
            relative_x = mouse_pos[0] - self.slider_rect.x
            self.slider_pos = max(0, min(relative_x, self.slider_rect.width))
            self.sides = int(3 + (self.slider_pos / self.slider_rect.width) * 9)
            self.original_polygon = self.create_polygon(self.sides, 75)
    
    def draw_slider(self):
        pygame.draw.rect(self.screen, SLIDER_BG, self.slider_rect, border_radius=5)
        handle_x = self.slider_rect.x + self.slider_pos
        handle_rect = pygame.Rect(handle_x - 5, self.slider_rect.y - 5, 10, 20)
        pygame.draw.rect(self.screen, SLIDER_HANDLE, handle_rect, border_radius=3)
        label = self.font.render(f"Sides: {self.sides}", True, TEXT_COLOR)
        self.screen.blit(label, (self.slider_rect.x, self.slider_rect.y - 30))
    
    def draw_instructions(self):
        instructions = [
            "Controls:",
            "--------------------",
            "Arrow Keys: Translate",
            "SHIFT + Arrows: Scale",
            "CTRL + Arrows: Rotate",
            "ALT + Arrows: Shear",
            "U / I: Reflect X / Y",
            "SPACE: Reset All"
        ]
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, TEXT_COLOR)
            self.screen.blit(text, (WIDTH - 200, 20 + i * 25))
    
    def handle_keys(self, keys):
        speed = 2
        scale_speed = 0.02
        rotate_speed = 0.03
        shear_speed = 0.02
        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_SHIFT:
            if keys[pygame.K_RIGHT]: self.sx += scale_speed
            if keys[pygame.K_LEFT]: self.sx = max(0.1, self.sx - scale_speed)
            if keys[pygame.K_UP]: self.sy += scale_speed
            if keys[pygame.K_DOWN]: self.sy = max(0.1, self.sy - scale_speed)
        elif mods & pygame.KMOD_CTRL:
            if keys[pygame.K_RIGHT]: self.angle += rotate_speed
            if keys[pygame.K_LEFT]: self.angle -= rotate_speed
        elif mods & pygame.KMOD_ALT:
            if keys[pygame.K_RIGHT]: self.shx += shear_speed
            if keys[pygame.K_LEFT]: self.shx -= shear_speed
            if keys[pygame.K_UP]: self.shy += shear_speed
            if keys[pygame.K_DOWN]: self.shy -= shear_speed
        else:
            if keys[pygame.K_UP]: self.ty += speed
            if keys[pygame.K_DOWN]: self.ty -= speed
            if keys[pygame.K_LEFT]: self.tx -= speed
            if keys[pygame.K_RIGHT]: self.tx += speed
    
    def reset(self):
        self.tx, self.ty = 0, 0
        self.sx, self.sy = 1, 1
        self.angle = 0
        self.shx, self.shy = 0, 0
        self.reflect_x, self.reflect_y = False, False
        self.sides = 6
        self.slider_pos = ((self.sides - 3) / 9) * self.slider_rect.width
        self.original_polygon = self.create_polygon(self.sides, 75)
        self.transformed_polygon = self.original_polygon.copy()
    
    def run(self):
        running = True
        mouse_pressed = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.reset()
                        continue
                    elif event.key == pygame.K_u:
                        self.reflect_x = not self.reflect_x
                    elif event.key == pygame.K_i:
                        self.reflect_y = not self.reflect_y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pressed = True
                        self.handle_slider(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_pressed = False
                elif event.type == pygame.MOUSEMOTION and mouse_pressed:
                    self.handle_slider(event.pos)
            
            keys = pygame.key.get_pressed()
            self.handle_keys(keys)
            self.apply_transformations()
            
            self.screen.fill(BG_COLOR)
            pygame.draw.line(self.screen, AXIS_COLOR, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)
            pygame.draw.line(self.screen, AXIS_COLOR, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 1)
            
            original_points = self.world_to_screen(self.original_polygon)
            if len(original_points) > 2:
                pygame.draw.polygon(self.screen, RED, original_points, 2)
            
            transformed_points = self.world_to_screen(self.transformed_polygon)
            if len(transformed_points) > 2:
                pygame.draw.polygon(self.screen, BLUE, transformed_points)
                pygame.draw.polygon(self.screen, TEXT_COLOR, transformed_points, 2)
            
            self.draw_slider()
            self.draw_instructions()
            
            values_text = [
                f"Translate: ({self.tx:.1f}, {self.ty:.1f})",
                f"Scale: ({self.sx:.2f}, {self.sy:.2f})",
                f"Rotate: {math.degrees(self.angle):.1f}°",
                f"Shear: ({self.shx:.2f}, {self.shy:.2f})",
                f"Reflect: [X: {self.reflect_x}, Y: {self.reflect_y}]"
            ]
            for i, text in enumerate(values_text):
                rendered = self.font.render(text, True, TEXT_COLOR)
                self.screen.blit(rendered, (20, 20 + i * 25))
            
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    app = Transform2D()
    app.run()
