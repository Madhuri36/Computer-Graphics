import pygame
import numpy as np
from dataclasses import dataclass
from typing import Optional, List

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
MAX_DEPTH = 3
EPSILON = 1e-6

@dataclass
class Vec3:
    x: float
    y: float
    z: float
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def length(self):
        return np.sqrt(self.dot(self))
    
    def normalize(self):
        l = self.length()
        return self / l if l > 0 else Vec3(0, 0, 0)
    
    def reflect(self, normal):
        return self - normal * (2 * self.dot(normal))
    
    def to_color(self):
        return (min(255, max(0, int(self.x * 255))),
                min(255, max(0, int(self.y * 255))),
                min(255, max(0, int(self.z * 255))))

@dataclass
class Ray:
    origin: Vec3
    direction: Vec3

@dataclass
class Material:
    color: Vec3
    ambient: float
    diffuse: float
    specular: float
    shininess: float
    reflection: float

@dataclass
class HitRecord:
    t: float
    point: Vec3
    normal: Vec3
    material: Material

class Sphere:
    def __init__(self, center: Vec3, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def intersect(self, ray: Ray) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return None
        
        t = (-b - np.sqrt(discriminant)) / (2.0 * a)
        if t < EPSILON:
            t = (-b + np.sqrt(discriminant)) / (2.0 * a)
            if t < EPSILON:
                return None
        
        point = ray.origin + ray.direction * t
        normal = (point - self.center).normalize()
        return HitRecord(t, point, normal, self.material)

class Plane:
    def __init__(self, point: Vec3, normal: Vec3, material: Material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material
    
    def intersect(self, ray: Ray) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < EPSILON:
            return None
        
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t < EPSILON:
            return None
        
        point = ray.origin + ray.direction * t
        return HitRecord(t, point, self.normal, self.material)

@dataclass
class Light:
    position: Vec3
    color: Vec3
    intensity: float

class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def add_light(self, light):
        self.lights.append(light)
    
    def intersect(self, ray: Ray) -> Optional[HitRecord]:
        closest_hit = None
        min_t = float('inf')
        
        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit and hit.t < min_t:
                min_t = hit.t
                closest_hit = hit
        
        return closest_hit

class RayTracer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        self.fov = np.pi / 3
        self.camera_pos = Vec3(0, 2, 10)
        
    def compute_lighting(self, scene: Scene, hit: HitRecord, ray_dir: Vec3, depth: int) -> Vec3:
        color = Vec3(0, 0, 0)
        mat = hit.material
        
        # Ambient
        color = mat.color * mat.ambient
        
        # Lighting from each light source
        for light in scene.lights:
            light_dir = (light.position - hit.point).normalize()
            light_distance = (light.position - hit.point).length()
            
            # Shadow ray
            shadow_ray = Ray(hit.point + hit.normal * EPSILON, light_dir)
            shadow_hit = scene.intersect(shadow_ray)
            
            if shadow_hit and shadow_hit.t < light_distance:
                continue  # In shadow
            
            # Diffuse
            diffuse_intensity = max(0, hit.normal.dot(light_dir))
            diffuse = mat.color * mat.diffuse * diffuse_intensity * light.intensity
            color = color + Vec3(diffuse.x * light.color.x,
                                diffuse.y * light.color.y,
                                diffuse.z * light.color.z)
            
            # Specular
            reflect_dir = light_dir.reflect(hit.normal)
            view_dir = (self.camera_pos - hit.point).normalize()
            spec_intensity = max(0, view_dir.dot(reflect_dir)) ** mat.shininess
            specular = light.color * mat.specular * spec_intensity * light.intensity
            color = color + specular
        
        # Reflection
        if mat.reflection > 0 and depth < MAX_DEPTH:
            reflect_dir = ray_dir.reflect(hit.normal)
            reflect_ray = Ray(hit.point + hit.normal * EPSILON, reflect_dir)
            reflect_color = self.trace_ray(scene, reflect_ray, depth + 1)
            color = color + reflect_color * mat.reflection
        
        return color
    
    def trace_ray(self, scene: Scene, ray: Ray, depth: int = 0) -> Vec3:
        if depth >= MAX_DEPTH:
            return Vec3(0, 0, 0)
        
        hit = scene.intersect(ray)
        if not hit:
            # Sky gradient
            t = 0.5 * (ray.direction.normalize().y + 1.0)
            return Vec3(0.5, 0.7, 1.0) * t + Vec3(1.0, 1.0, 1.0) * (1.0 - t)
        
        return self.compute_lighting(scene, hit, ray.direction, depth)
    
    def render(self, scene: Scene, screen):
        for y in range(self.height):
            for x in range(self.width):
                # Calculate ray direction
                px = (2 * (x + 0.5) / self.width - 1) * np.tan(self.fov / 2) * self.aspect_ratio
                py = (1 - 2 * (y + 0.5) / self.height) * np.tan(self.fov / 2)
                
                direction = Vec3(px, py, -1).normalize()
                ray = Ray(self.camera_pos, direction)
                
                # Trace ray
                color = self.trace_ray(scene, ray)
                screen.set_at((x, y), color.to_color())
            
            # Update display and window title with percentage
            if y % 5 == 0:
                percentage = (y / self.height) * 100
                pygame.display.set_caption(f"Ray Tracer - Rendering... {percentage:.1f}%")
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                
                # Print to console as well
                print(f"\rRendering: {percentage:.1f}%", end="", flush=True)
        
        print("\rRendering: 100.0%")
        return True

def create_scene():
    scene = Scene()
    
    # Materials
    red_shiny = Material(Vec3(0.8, 0.1, 0.1), 0.1, 0.7, 0.5, 32, 0.3)
    blue_matte = Material(Vec3(0.1, 0.3, 0.8), 0.1, 0.9, 0.1, 8, 0.1)
    green_reflective = Material(Vec3(0.1, 0.8, 0.1), 0.1, 0.6, 0.8, 64, 0.5)
    white_floor = Material(Vec3(0.8, 0.8, 0.8), 0.2, 0.8, 0.2, 16, 0.2)
    
    # Objects
    scene.add_object(Sphere(Vec3(0, 1, 0), 1, red_shiny))
    scene.add_object(Sphere(Vec3(-2.5, 0.7, -1), 0.7, blue_matte))
    scene.add_object(Sphere(Vec3(2, 0.8, -0.5), 0.8, green_reflective))
    scene.add_object(Plane(Vec3(0, 0, 0), Vec3(0, 1, 0), white_floor))
    
    # Lights
    scene.add_light(Light(Vec3(5, 5, 5), Vec3(1, 1, 1), 1.0))
    scene.add_light(Light(Vec3(-3, 3, 3), Vec3(1, 0.9, 0.8), 0.6))
    
    return scene

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ray Tracer - Rendering...")
    
    # Create scene
    scene = create_scene()
    
    # Create ray tracer
    tracer = RayTracer(WIDTH, HEIGHT)
    
    # Render
    print("Rendering scene... This may take a minute.")
    if tracer.render(scene, screen):
        pygame.display.set_caption("Ray Tracer - Complete!")
        pygame.display.flip()
        print("Rendering complete!")
        
        # Keep window open
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()