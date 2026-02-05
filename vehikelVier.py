import math
import random
import pygame
import sys

WIDTH, HEIGHT = 1480, 720
BG_COLOR = (15, 15, 25)

LIGHT_COLOR = (255, 215, 0)
V4A_COLOR = (255, 160, 40)       # 4a orange
V4B_COLOR = (200, 120, 255)      # 4b purple


# shows how storng is the sources at a distance
def gaussian_intensity(dist, radius, strength):
    if dist > radius:
        return 0.0
    v = max(0.0, 1.0 - (dist / radius) ** 2)
    return v * strength


# source
class Source:
    def __init__(self, x, y, stype="light",
                 strength=1.2, radius=260):
        self.x = x
        self.y = y
        self.type = stype
        self.strength = strength
        self.radius = radius

    def pos(self):
        return (self.x, self.y)

    def draw(self, surf):
        if self.type == "light":
            pygame.draw.circle(
                surf, LIGHT_COLOR, (int(self.x), int(self.y)), 22)
            pygame.draw.circle(
                surf, (255, 255, 0), (int(self.x), int(self.y)), 5)

# vehicle body
class BraitenbergVehicle:
    """
    Types:
      "4a": non-monotonic (values / special tastes)
      "4b": threshold / step-like (decisions, will) [web:1][web:40][web:43]
    """

    def __init__(self, x, y, vtype="4a", color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.vtype = vtype
        self.color = color

        self.base_speed = 70.0
        self.wheel_base = 40.0
        self.sensor_offset = 25.0
        self.sensor_side_offset = 18.0

# shows where the left and right sensors are in space
    def sensor_positions(self):
        fx = math.cos(self.angle) * self.sensor_offset
        fy = math.sin(self.angle) * self.sensor_offset

        px = -math.sin(self.angle) * self.sensor_side_offset
        py = math.cos(self.angle) * self.sensor_side_offset

        left = (self.x + fx + px, self.y + fy + py)
        right = (self.x + fx - px, self.y + fy - py)
        return left, right


# measures total light at left and right sensors
    def read_light_pair(self, light_sources):
        left_pos, right_pos = self.sensor_positions()
        sL = sR = 0.0
        for s in light_sources:
            sx, sy = s.pos()
            dL = math.dist((sx, sy), left_pos)
            dR = math.dist((sx, sy), right_pos)
            sL += gaussian_intensity(dL, s.radius, s.strength)
            sR += gaussian_intensity(dR, s.radius, s.strength)
        return sL, sR

    def step(self, dt, light_sources):
        if self.vtype == "4a":
            self.step_4a(dt, light_sources)
        else:
            self.step_4b(dt, light_sources)

        self.x %= WIDTH
        self.y %= HEIGHT

    # 4a non‑monotonic



    def nonmonotonic_response(self, I, I_pref=0.8, width=0.6, gain=170.0):
        """
        Bell‑shaped tuning: speeds up as intensity approaches I_pref,
        then slows again when intensity is too strong or too weak. [web:1][web:40][web:43]
        """
        if I <= 0:
            return 0.0
        d = (I - I_pref) / width
        return gain * math.exp(-d * d)

    def step_4a(self, dt, light_sources):
        """
        4a: crossed excitatory wiring (like 2b) + non‑monotonic response.
        Produces orbits / figure‑eight trajectories near the light. [web:1][web:40]
        """
        sL, sR = self.read_light_pair(light_sources)

        # crossed: left sensor → right motor, right sensor → left motor
        vL = self.base_speed + self.nonmonotonic_response(sR)
        vR = self.base_speed + self.nonmonotonic_response(sL)

        vL = max(-120.0, min(260.0, vL))
        vR = max(-120.0, min(260.0, vR))
        self.apply_wheel_speeds(dt, vL, vR)

    # 4b threshold

        # the step graph
            # below threshold, nothing happens
            # above threshold, suddend activation
    def threshold_response(self, I, thr=0.4, max_gain=220.0):
        """
        4b: no activation below threshold; strong activation above.
        Looks like a 'decision' to start moving. [web:1][web:25][web:43]
        """
        if I < thr:
            return 0.0
        base = 60.0
        return min(max_gain, base + (I - thr) * 200.0)

        # excitatory wiring
            # the curve graph with a break
            # hesitation, decision, will
    def step_4b(self, dt, light_sources):
        sL, sR = self.read_light_pair(light_sources)

        # ipsilateral excitatory with threshold
        vL = self.base_speed + self.threshold_response(sL)
        vR = self.base_speed + self.threshold_response(sR)

        vL = max(0.0, min(260.0, vL))
        vR = max(0.0, min(260.0, vR))
        self.apply_wheel_speeds(dt, vL, vR)


        # apply wwheel speed
    def apply_wheel_speeds(self, dt, vL, vR):
        v = 0.5 * (vL + vR)
        omega = (vR - vL) / self.wheel_base
        self.angle = (self.angle + omega * dt) % (2 * math.pi)
        self.x += math.cos(self.angle) * v * dt
        self.y += math.sin(self.angle) * v * dt

    def draw(self, surf, font_small):
        radius = 28
        pygame.draw.circle(
            surf, self.color, (int(self.x), int(self.y)), radius
        )

        hx = self.x + math.cos(self.angle) * radius
        hy = self.y + math.sin(self.angle) * radius
        pygame.draw.line(
            surf, (255, 255, 255),
            (self.x, self.y), (hx, hy), 3
        )

        left_s, right_s = self.sensor_positions()
        pygame.draw.circle(surf, (255, 255, 255), left_s, 4)
        pygame.draw.circle(surf, (255, 255, 255), right_s, 4)

        label = "4a VALUES" if self.vtype == "4a" else "4b THRESH"
        text = font_small.render(label, True, (255, 255, 255))
        surf.blit(text, (self.x - text.get_width() / 2,
                         self.y - radius - 18))

def main():
    pygame.init()
    pygame.display.set_caption(
        "Braitenberg Vehicles — 4a/4b only"
    )
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 19)
    font_small = pygame.font.SysFont("consolas", 15)

    light_sources = []

    vehicles = []
    x_start = 260
    dx = 260
    # three columns of each type
    for i in range(4):
        x = x_start + dx * i
        vehicles.append(BraitenbergVehicle(x, 320, "4a", V4A_COLOR))
        vehicles.append(BraitenbergVehicle(x, 520, "4b", V4B_COLOR))

    dragging_light = None
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 3:   # right click -> new light
                    light_sources.append(
                        Source(mx, my, "light", 1.2, 260)
                    )
                elif event.button == 1:  # left click -> drag nearest light
                    for src in light_sources:
                        if math.dist((mx, my), src.pos()) <= 26:
                            dragging_light = src
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_light = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_light is not None:
                    mx, my = pygame.mouse.get_pos()
                    dragging_light.x = mx
                    dragging_light.y = my

        for v in vehicles:
            v.step(dt, light_sources)

        screen.fill(BG_COLOR)

        title = font.render(
            "Right-click: add LIGHT   Left-drag: move light   Esc: quit",
            True, (235, 235, 235),
        )
        screen.blit(title, (10, 8))

        info = font_small.render(
            "4a: non-monotonic 'values'; 4b: threshold / decision-like behavior around light sources.",
            True, (210, 210, 210),
        )
        screen.blit(info, (10, 32))

        for s in light_sources:
            s.draw(screen)

        for v in vehicles:
            v.draw(screen, font_small)

        legend_lines = [
            "Legend:",
            "4a (ORANGE) — NON-MONOTONIC: crossed excitatory with preferred distance; can orbit / figure-eight.",
            "4b (PURPLE) — THRESHOLD: no motion below light threshold; fast motion above, like decisions / will.",
        ]
        box_x, box_y = 10, HEIGHT - 90
        box_w, box_h = 980, 80
        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, (230, 230, 230),
                         (box_x, box_y, box_w, box_h), 1)
        for i, line in enumerate(legend_lines):
            t = font_small.render(line, True, (230, 230, 230))
            screen.blit(t, (box_x + 8, box_y + 6 + 21 * i))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()