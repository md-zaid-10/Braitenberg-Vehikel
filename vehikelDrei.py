import math
import random
import pygame
import sys

WIDTH, HEIGHT = 1480, 720
BG_COLOR = (15, 15, 25)
LIGHT_COLOR = (255, 215, 0)
LOVE_COLOR = (80, 210, 120)
EXPLORE_COLOR = (60, 150, 255)
COMPLEX_COLOR = (250, 80, 80)


# How light works
def gaussian_intensity(dist, radius, strength):
    if dist > radius:
        return 0.0
    v = max(0.0, 1.0 - (dist / radius) ** 2)
    return v * strength

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

class BraitenbergVehicle:

    # vehicle 3a
    def __init__(self, x, y, vtype="3a", color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.vtype = vtype
        self.color = color
        self.base_speed = 70.0
        self.wheel_base = 40.0
        self.sensor_offset = 25.0
        self.sensor_side_offset = 18.0
        self.connections_3c = {}
        self.setup_3c_connections()

# vehicle 3c wiring
    def setup_3c_connections(self):
        w_ex = 90.0
        w_inh = -95.0
        types = ["light", "heat", "oxygen", "organic"]
        for t in types:
            for s in ["L", "R"]:
                for m in ["L", "R"]:
                    self.connections_3c[(t, s, m)] = 0.0

        self.connections_3c[("light", "L", "L")] = w_ex
        self.connections_3c[("light", "R", "R")] = w_ex
        self.connections_3c[("heat", "L", "R")] = w_ex
        self.connections_3c[("heat", "R", "L")] = w_ex
        self.connections_3c[("oxygen", "L", "R")] = w_inh
        self.connections_3c[("oxygen", "R", "L")] = w_inh
        self.connections_3c[("organic", "L", "L")] = w_inh
        self.connections_3c[("organic", "R", "R")] = w_inh

    def sensor_positions(self):
        fx = math.cos(self.angle) * self.sensor_offset
        fy = math.sin(self.angle) * self.sensor_offset
        px = -math.sin(self.angle) * self.sensor_side_offset
        py = math.cos(self.angle) * self.sensor_side_offset
        left = (self.x + fx + px, self.y + fy + py)
        right = (self.x + fx - px, self.y + fy - py)
        return left, right

    def read_sensors(self, sources):
        left_pos, right_pos = self.sensor_positions()
        values = {
            ("light", "L"): 0.0, ("light", "R"): 0.0,
            ("heat", "L"): 0.0, ("heat", "R"): 0.0,
            ("oxygen", "L"): 0.0, ("oxygen", "R"): 0.0,
            ("organic", "L"): 0.0, ("organic", "R"): 0.0,
        }

        for s in sources:
            sx, sy = s.pos()
            dL = math.dist((sx, sy), left_pos)
            dR = math.dist((sx, sy), right_pos)
            vL = gaussian_intensity(dL, s.radius, s.strength)
            vR = gaussian_intensity(dR, s.radius, s.strength)
            values[(s.type, "L")] += vL
            values[(s.type, "R")] += vR
        return values

    def step(self, dt, sources):
        if self.vtype in ("3a", "3b"):
            light_sources = [s for s in sources if s.type == 'light']
            self.step_simple(dt, light_sources)
        else:
            self.step_3c(dt, sources)
        self.x %= WIDTH
        self.y %= HEIGHT

    def simple_weight_matrix(self):
        w_inh = -140.0
        if self.vtype == "3a":
            return {("L", "L"): w_inh, ("R", "R"): w_inh}
        else:
            return {("L", "R"): w_inh, ("R", "L"): w_inh}


#vehicle 3a and 3b behaviour
    def step_simple(self, dt, light_sources):
        left_pos, right_pos = self.sensor_positions()
        sL = sR = 0.0
        for s in light_sources:
            sx, sy = s.pos()
            dL = math.dist((sx, sy), left_pos)
            dR = math.dist((sx, sy), right_pos)
            sL += gaussian_intensity(dL, s.radius, s.strength)
            sR += gaussian_intensity(dR, s.radius, s.strength)

        weights = self.simple_weight_matrix()
        vL = self.base_speed
        vR = self.base_speed
        vL += weights.get(("L", "L"), 0.0) * sL
        vL += weights.get(("R", "L"), 0.0) * sR
        vR += weights.get(("L", "R"), 0.0) * sL
        vR += weights.get(("R", "R"), 0.0) * sR
        vL = max(-120.0, min(230.0, vL))
        vR = max(-120.0, min(230.0, vR))
        self.apply_wheel_speeds(dt, vL, vR)


# Vehicle 3c behavior
    def step_3c(self, dt, all_sources):
        sensors = self.read_sensors(all_sources)
        vL = self.base_speed
        vR = self.base_speed
        for (stype, side), sval in sensors.items():
            for mside in ("L", "R"):
                w = self.connections_3c[(stype, side, mside)]
                if mside == "L":
                    vL += w * sval
                else:
                    vR += w * sval
        vL = max(-150.0, min(230.0, vL))
        vR = max(-150.0, min(230.0, vR))
        self.apply_wheel_speeds(dt, vL, vR)

# converts wheel speed into translation
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

        if self.vtype == "3a":
            label = "3a LOVE"
        elif self.vtype == "3b":
            label = "3b EXPLORE"
        else:
            label = "3c COMPLEX"
        text = font_small.render(label, True, (255, 255, 255))
        surf.blit(text, (self.x - text.get_width() / 2,
                        self.y - radius - 18))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Braitenberg Vehicles")
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont("Arial", 14)

    sources = [Source(WIDTH / 2, HEIGHT / 2, "light")]

    vehicles = []
    for _ in range(5):
        vehicles.append(BraitenbergVehicle(
            random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
            vtype="3a", color=LOVE_COLOR
        ))
        vehicles.append(BraitenbergVehicle(
            random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
            vtype="3b", color=EXPLORE_COLOR
        ))
        vehicles.append(BraitenbergVehicle(
            random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
            vtype="3c", color=COMPLEX_COLOR
        ))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    sources.append(Source(mouse_x, mouse_y, "light"))

        for v in vehicles:
            v.step(dt, sources)

        screen.fill(BG_COLOR)
        for s in sources:
            s.draw(screen)
        for v in vehicles:
            v.draw(screen, font_small)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()