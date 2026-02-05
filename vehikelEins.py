import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle - Random Wandering")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  
BLUE = (0, 0, 255) 
BACKGROUND = (20, 20, 40)

font = pygame.font.SysFont(None, 24)

class LightSource:
    def __init__(self, position, radius=30, color=BLUE, intensity=150):  # Changed to BLUE
        self.position = position
        self.radius = radius
        self.color = color
        self.intensity = intensity

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

class Vehicle:
    def __init__(self, position, radius=25, color=GREEN, direction=0):  # Changed to GREEN
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

    #creates a vector pointing forward relative to vehicles direction
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

    #speed increase near the source of light vive versa
    def sense_light(self, lights):
        self.sensor_value = 0
        for light in lights:
            distance = pygame.math.Vector2(light.position).distance_to(self.sensor_position)
            if distance > 0:
                self.sensor_value += light.intensity / (distance * distance / 1000)

    # direction changes -60 to +60
    def move(self, lights):
        self.sense_light(lights)

        # Randomly change direction angles to -60 and +60 degrees randomly
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

# Initial setup
light_sources = [LightSource((600, 300), radius=25, intensity=250)]
vehicle = Vehicle((300, 400), 30, GREEN, random.uniform(0, 360))  # Changed to GREEN
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
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_light = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_light:
                dragging_light.position = event.pos

    screen.fill(BACKGROUND)
    for light in light_sources:
        light.draw(screen)
    vehicle.move(light_sources)
    vehicle.draw(screen)

    instructions = [
        "Braitenberg Vehicle - Random Wander Mode",
        "Moves freely; reacts to light intensity (faster near light)",
        "Left-click and drag: Move light source"
    ]
    y_offset = 60
    for line in instructions:
        text = font.render(line, True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 25

    pygame.display.flip()
    clock.tick(60)

pygame.quit()