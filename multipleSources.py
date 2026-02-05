import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle - Multiple Light Sources")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BACKGROUND = (20, 20, 40)

font = pygame.font.SysFont(None, 24)

class LightSource:
    def __init__(self, position, radius=30, color=BLUE, intensity=150):
        self.position = position
        self.radius = radius
        self.color = color
        self.intensity = intensity

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

class Vehicle:
    def __init__(self, position, radius=25, color=GREEN, direction=0):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.sensor_offset = self.radius + 10
        self.sensor_radius = 8
        self.sensor_color = BLUE
        self.sensor_value = 0
        self.turn_timer = 0
        self.update_sensor_position()

    def update_sensor_position(self):
        forward = pygame.math.Vector2(0, -self.sensor_offset).rotate(self.direction)
        self.sensor_position = self.position + forward

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        front = self.position + pygame.math.Vector2(0, -self.radius).rotate(self.direction)
        pygame.draw.line(surface, WHITE, self.position, front, 2)
        pygame.draw.circle(surface, self.sensor_color, (int(self.sensor_position.x), int(self.sensor_position.y)), self.sensor_radius)
        sensor_text = font.render(f"S: {self.sensor_value:.1f}", True, WHITE)
        surface.blit(sensor_text, (self.sensor_position.x - 20, self.sensor_position.y - 25))

    def sense_light(self, lights):
        self.sensor_value = 0
        for light in lights:
            distance = pygame.math.Vector2(light.position).distance_to(self.sensor_position)
            if distance > 0:
                self.sensor_value += light.intensity / (distance * distance / 1000)

    def move(self, lights):
        self.sense_light(lights)

        # Randomly change direction
        self.turn_timer += 1
        if self.turn_timer > random.randint(40, 120):
            self.direction += random.uniform(-60, 60)
            self.turn_timer = 0

        # Speed affected by light intensity but not fixed direction
        base_speed = 2
        speed = base_speed + min(self.sensor_value * 0.03, 8.0)

        movement = pygame.math.Vector2(0, -speed).rotate(self.direction)
        self.position += movement

        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        self.update_sensor_position()

        speed_text = font.render(f"Speed: {speed:.1f}", True, WHITE)
        heading_text = font.render(f"Heading: {self.direction:.1f}°", True, WHITE)
        screen.blit(speed_text, (10, 10))
        screen.blit(heading_text, (10, 30))

# Initial setup with multiple lights
light_sources = [
    LightSource((600, 300), radius=25, intensity=250),
    LightSource((200, 200), radius=20, intensity=180),
    LightSource((1000, 400), radius=30, intensity=300)
]
vehicle = Vehicle((300, 400), 30, GREEN, random.uniform(0, 360))
dragging_light = None
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for light in light_sources:
                if pygame.math.Vector2(mouse_pos).distance_to(light.position) < light.radius:
                    dragging_light = light
                    break
            # Right-click to add new light
            if event.button == 3:  # Right mouse button
                new_light = LightSource(mouse_pos, radius=random.randint(15, 35), 
                                      intensity=random.randint(100, 350))
                light_sources.append(new_light)
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_light = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_light:
                dragging_light.position = event.pos
        elif event.type == pygame.KEYDOWN:
            # Press 'a' to add random light
            if event.key == pygame.K_a:
                new_x = random.randint(50, WIDTH-50)
                new_y = random.randint(50, HEIGHT-50)
                new_light = LightSource((new_x, new_y), 
                                      radius=random.randint(15, 35),
                                      intensity=random.randint(100, 350))
                light_sources.append(new_light)
            # Press 'd' to delete last light
            elif event.key == pygame.K_d and light_sources:
                light_sources.pop()
            # Press 'c' to clear all lights
            elif event.key == pygame.K_c:
                light_sources.clear()
            # Press spacebar to add light at vehicle position
            elif event.key == pygame.K_SPACE:
                new_light = LightSource((int(vehicle.position.x), int(vehicle.position.y)),
                                      radius=20, intensity=200)
                light_sources.append(new_light)

    screen.fill(BACKGROUND)
    
    # Draw all light sources
    for i, light in enumerate(light_sources):
        light.draw(screen)
        # Show light info
        light_text = font.render(f"Light {i+1}: {light.intensity}", True, WHITE)
        screen.blit(light_text, (light.position.x - 30, light.position.y + light.radius + 5))
    
    vehicle.move(light_sources)
    vehicle.draw(screen)

    instructions = [
        "Braitenberg Vehicle - Multiple Light Sources",
        "Moves freely; reacts to light intensity (faster near light)",
        "Controls:",
        "Left-click and drag: Move light source",
        "Right-click: Add new light at mouse position",
        "A key: Add random light",
        "D key: Delete last light", 
        "C key: Clear all lights",
        "Spacebar: Add light at vehicle position",
        f"Current lights: {len(light_sources)}"
    ]
    y_offset = 60
    for line in instructions:
        text = font.render(line, True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 25

    pygame.display.flip()
    clock.tick(60)

pygame.quit()