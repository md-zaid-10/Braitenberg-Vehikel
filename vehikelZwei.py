import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicles - Fear & Aggression")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
BACKGROUND = (20, 20, 40)

font = pygame.font.SysFont(None, 24)

class LightSource:
    def __init__(self, position, radius=30, color=YELLOW, intensity=150):
        self.position = position
        self.radius = radius
        self.color = color
        self.intensity = intensity

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)

class Vehicle:
    def __init__(self, position, radius=25, color=RED, direction=0, behavior="fear"):
        self.position = pygame.math.Vector2(position)
        self.direction = direction
        self.radius = radius
        self.color = color
        self.behavior = behavior
        self.sensor_offset = self.radius + 10
        self.sensor_separation = 30
        self.sensor_radius = 8
        self.sensor_color = YELLOW
        self.left_sensor_value = 0
        self.right_sensor_value = 0
        self.turn_timer = 0
        self.update_sensor_positions()

    def update_sensor_positions(self):
        left_offset = pygame.math.Vector2(-self.sensor_separation / 2, -self.sensor_offset)
        right_offset = pygame.math.Vector2(self.sensor_separation / 2, -self.sensor_offset)
        self.left_sensor_position = self.position + left_offset.rotate(self.direction)
        self.right_sensor_position = self.position + right_offset.rotate(self.direction)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        front = self.position + pygame.math.Vector2(0, -self.radius).rotate(self.direction)
        pygame.draw.line(surface, WHITE, self.position, front, 2)
        pygame.draw.circle(surface, self.sensor_color, (int(self.left_sensor_position.x), int(self.left_sensor_position.y)), self.sensor_radius)
        pygame.draw.circle(surface, self.sensor_color, (int(self.right_sensor_position.x), int(self.right_sensor_position.y)), self.sensor_radius)
        left_text = font.render(f"L: {self.left_sensor_value:.1f}", True, WHITE)
        right_text = font.render(f"R: {self.right_sensor_value:.1f}", True, WHITE)
        surface.blit(left_text, (self.left_sensor_position.x - 25, self.left_sensor_position.y - 25))
        surface.blit(right_text, (self.right_sensor_position.x - 25, self.right_sensor_position.y - 25))
        behavior_text = font.render(f"{self.behavior.upper()}", True, WHITE)
        surface.blit(behavior_text, (self.position.x - 25, self.position.y + self.radius + 5))

    def sense_light(self, lights):
        self.left_sensor_value = 0
        self.right_sensor_value = 0
        for light in lights:
            left_dist = pygame.math.Vector2(light.position).distance_to(self.left_sensor_position)
            right_dist = pygame.math.Vector2(light.position).distance_to(self.right_sensor_position)
            if left_dist > 0:
                self.left_sensor_value += light.intensity / (left_dist * left_dist / 1000)
            if right_dist > 0:
                self.right_sensor_value += light.intensity / (right_dist * right_dist / 1000)

    def move(self, lights):
        self.sense_light(lights)
        base_speed = 2

        if self.behavior == "fear":
            left_wheel_speed = base_speed + min(self.right_sensor_value * 0.03, 8.0)
            right_wheel_speed = base_speed + min(self.left_sensor_value * 0.03, 8.0)
        elif self.behavior == "aggression":
            left_wheel_speed = base_speed + min(self.left_sensor_value * 0.03, 8.0)
            right_wheel_speed = base_speed + min(self.right_sensor_value * 0.03, 8.0)
        else:
            left_wheel_speed = right_wheel_speed = base_speed

        #turning
        speed = (left_wheel_speed + right_wheel_speed) / 2
        rotation = (right_wheel_speed - left_wheel_speed) * 0.8
        self.turn_timer += 1
        if self.turn_timer > random.randint(40, 120):
            self.direction += random.uniform(-60, 60)
            self.turn_timer = 0
        self.direction += rotation
        movement = pygame.math.Vector2(0, -speed).rotate(self.direction)
        self.position += movement
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        self.update_sensor_positions()

light_sources = [LightSource((600, 300), radius=25, intensity=250)]
vehicles = [
    Vehicle((300, 400), 30, RED, random.uniform(0, 360), behavior="fear"),
    Vehicle((800, 200), 30, BLUE, random.uniform(0, 360), behavior="aggression")
]

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
                
            #mouse right click
            if event.button == 3 and dragging_light is None:
                light_sources.append(LightSource(mouse_pos, radius=25, intensity=200))
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_light = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_light:
                dragging_light.position = event.pos

    screen.fill(BACKGROUND)
    for light in light_sources:
        light.draw(screen)
    for v in vehicles:
        v.move(light_sources)
        v.draw(screen)
    instructions = [
        "Braitenberg Vehicles - Fear & Aggression",
        "Red: Fear (moves away from light)",
        "Blue: Aggression (moves toward light)",
        "Right-click: Add new light source",
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