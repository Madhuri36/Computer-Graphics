import pygame
import numpy as np
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

class Transform2D:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2D Transformations")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Original object (a simple house shape)
        self.original_points = np.array([
            [100, 150],  # Bottom left
            [200, 150],  # Bottom right
            [200, 100],  # Top right of base
            [150, 50],   # Roof peak
            [100, 100],  # Top left of base
            [100, 150]   # Close the shape
        ], dtype=float)
        
        self.transformed_points = self.original_points.copy()
        
    def translate(self, tx, ty):
        """Translation transformation"""
        translation_matrix = np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ])
        return translation_matrix
    
    def scale(self, sx, sy, cx=0, cy=0):
        """Scaling transformation around a center point"""
        # Translate to origin, scale, then translate back
        t1 = self.translate(-cx, -cy)
        s = np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ])
        t2 = self.translate(cx, cy)
        return t2 @ s @ t1
    
    def rotate(self, angle, cx=0, cy=0):
        """Rotation transformation around a center point"""
        # Convert angle to radians
        theta = math.radians(angle)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        
        # Translate to origin, rotate, then translate back
        t1 = self.translate(-cx, -cy)
        r = np.array([
            [cos_theta, -sin_theta, 0],
            [sin_theta, cos_theta, 0],
            [0, 0, 1]
        ])
        t2 = self.translate(cx, cy)
        return t2 @ r @ t1
    
    def reflect_x(self):
        """Reflection across X-axis"""
        return np.array([
            [1, 0, 0],
            [0, -1, 0],
            [0, 0, 1]
        ])
    
    def reflect_y(self):
        """Reflection across Y-axis"""
        return np.array([
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
    
    def shear_x(self, shx):
        """Shearing along X-axis"""
        return np.array([
            [1, shx, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
    
    def shear_y(self, shy):
        """Shearing along Y-axis"""
        return np.array([
            [1, 0, 0],
            [shy, 1, 0],
            [0, 0, 1]
        ])
    
    def apply_transformation(self, matrix):
        """Apply transformation matrix to points"""
        # Convert to homogeneous coordinates
        homogeneous_points = np.column_stack((self.transformed_points, np.ones(len(self.transformed_points))))
        
        # Apply transformation
        transformed_homogeneous = (matrix @ homogeneous_points.T).T
        
        # Convert back to 2D coordinates
        self.transformed_points = transformed_homogeneous[:, :2]
    
    def reset(self):
        """Reset to original shape"""
        self.transformed_points = self.original_points.copy()
    
    def draw_points(self, points, color, width=2):
        """Draw the shape from points"""
        if len(points) > 1:
            pygame.draw.lines(self.screen, color, False, points, width)
    
    def draw_grid(self):
        """Draw coordinate grid"""
        for x in range(0, WINDOW_WIDTH, 50):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, 50):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw axes
        pygame.draw.line(self.screen, BLACK, (0, WINDOW_HEIGHT//2), (WINDOW_WIDTH, WINDOW_HEIGHT//2), 2)
        pygame.draw.line(self.screen, BLACK, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT), 2)
    
    def draw_instructions(self):
        """Draw instruction text"""
        instructions = [
            "2D TRANSFORMATIONS - CONTROLS:",
            "T + Arrow Keys: Translation",
            "S + Up/Down: Scale up/down",
            "R + Left/Right: Rotate",
            "X: Reflect across X-axis",
            "Y: Reflect across Y-axis",
            "H + Left/Right: Shear X",
            "V + Up/Down: Shear Y",
            "SPACE: Reset",
            "ESC: Exit"
        ]
        
        y_offset = 10
        for instruction in instructions:
            text = self.small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (WINDOW_WIDTH - 250, y_offset))
            y_offset += 25
    
    def get_user_input(self):
        """Handle user input for transformations"""
        keys = pygame.key.get_pressed()
        
        # Translation
        if keys[pygame.K_t]:
            if keys[pygame.K_UP]:
                matrix = self.translate(0, -5)
                self.apply_transformation(matrix)
            elif keys[pygame.K_DOWN]:
                matrix = self.translate(0, 5)
                self.apply_transformation(matrix)
            elif keys[pygame.K_LEFT]:
                matrix = self.translate(-5, 0)
                self.apply_transformation(matrix)
            elif keys[pygame.K_RIGHT]:
                matrix = self.translate(5, 0)
                self.apply_transformation(matrix)
        
        # Scaling
        elif keys[pygame.K_s]:
            center_x = np.mean(self.transformed_points[:, 0])
            center_y = np.mean(self.transformed_points[:, 1])
            if keys[pygame.K_UP]:
                matrix = self.scale(1.05, 1.05, center_x, center_y)
                self.apply_transformation(matrix)
            elif keys[pygame.K_DOWN]:
                matrix = self.scale(0.95, 0.95, center_x, center_y)
                self.apply_transformation(matrix)
        
        # Rotation
        elif keys[pygame.K_r]:
            center_x = np.mean(self.transformed_points[:, 0])
            center_y = np.mean(self.transformed_points[:, 1])
            if keys[pygame.K_LEFT]:
                matrix = self.rotate(-2, center_x, center_y)
                self.apply_transformation(matrix)
            elif keys[pygame.K_RIGHT]:
                matrix = self.rotate(2, center_x, center_y)
                self.apply_transformation(matrix)
        
        # Shearing X
        elif keys[pygame.K_h]:
            if keys[pygame.K_LEFT]:
                matrix = self.shear_x(-0.02)
                self.apply_transformation(matrix)
            elif keys[pygame.K_RIGHT]:
                matrix = self.shear_x(0.02)
                self.apply_transformation(matrix)
        
        # Shearing Y
        elif keys[pygame.K_v]:
            if keys[pygame.K_UP]:
                matrix = self.shear_y(-0.02)
                self.apply_transformation(matrix)
            elif keys[pygame.K_DOWN]:
                matrix = self.shear_y(0.02)
                self.apply_transformation(matrix)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.reset()
                elif event.key == pygame.K_x:
                    center_y = np.mean(self.transformed_points[:, 1])
                    # Reflect across horizontal line through center
                    matrix = self.translate(0, -center_y) @ self.reflect_x() @ self.translate(0, center_y)
                    self.apply_transformation(matrix)
                elif event.key == pygame.K_y:
                    center_x = np.mean(self.transformed_points[:, 0])
                    # Reflect across vertical line through center
                    matrix = self.translate(-center_x, 0) @ self.reflect_y() @ self.translate(center_x, 0)
                    self.apply_transformation(matrix)
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        print("2D Transformations Program Started!")
        print("Use the following controls:")
        print("- T + Arrow Keys: Translation")
        print("- S + Up/Down: Scale")
        print("- R + Left/Right: Rotate")
        print("- X: Reflect across X-axis")
        print("- Y: Reflect across Y-axis")
        print("- H + Left/Right: Shear X")
        print("- V + Up/Down: Shear Y")
        print("- SPACE: Reset")
        print("- ESC: Exit")
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Handle continuous input
            self.get_user_input()
            
            # Clear screen
            self.screen.fill(WHITE)
            
            # Draw grid
            self.draw_grid()
            
            # Draw original shape (in red)
            self.draw_points(self.original_points, RED, 2)
            
            # Draw transformed shape (in blue)
            self.draw_points(self.transformed_points, BLUE, 3)
            
            # Draw instructions
            self.draw_instructions()
            
            # Draw title
            title = self.font.render("2D Transformations Demo", True, BLACK)
            self.screen.blit(title, (10, 10))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def demonstrate_transformations():
    """Demonstrate each transformation type"""
    print("\n=== 2D TRANSFORMATIONS DEMONSTRATION ===")
    transform = Transform2D()
    
    # Show original points
    print(f"Original points:\n{transform.original_points}")
    
    # Translation example
    print(f"\n1. TRANSLATION by (50, 30):")
    matrix = transform.translate(50, 30)
    transform.apply_transformation(matrix)
    print(f"Translated points:\n{transform.transformed_points}")
    
    # Reset and scale
    transform.reset()
    print(f"\n2. SCALING by (1.5, 1.5) around center:")
    center_x = np.mean(transform.original_points[:, 0])
    center_y = np.mean(transform.original_points[:, 1])
    matrix = transform.scale(1.5, 1.5, center_x, center_y)
    transform.apply_transformation(matrix)
    print(f"Scaled points:\n{transform.transformed_points}")
    
    # Reset and rotate
    transform.reset()
    print(f"\n3. ROTATION by 45 degrees around center:")
    matrix = transform.rotate(45, center_x, center_y)
    transform.apply_transformation(matrix)
    print(f"Rotated points:\n{transform.transformed_points}")
    
    # Reset and reflect
    transform.reset()
    print(f"\n4. REFLECTION across Y-axis:")
    matrix = transform.reflect_y()
    transform.apply_transformation(matrix)
    print(f"Reflected points:\n{transform.transformed_points}")
    
    # Reset and shear
    transform.reset()
    print(f"\n5. SHEARING along X-axis (factor 0.5):")
    matrix = transform.shear_x(0.5)
    transform.apply_transformation(matrix)
    print(f"Sheared points:\n{transform.transformed_points}")

if __name__ == "__main__":
    # First demonstrate transformations mathematically
    demonstrate_transformations()
    
    print("\n" + "="*50)
    print("Starting interactive visualization...")
    print("Close the window or press ESC to exit.")
    
    # Then run interactive visualization
    transform_app = Transform2D()
    transform_app.run()