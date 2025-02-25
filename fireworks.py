import pygame
import random
import math  # For trigonometric functions
from settings import *

class FireworkParticle:
    def __init__(self, x, y):
        # Corrected from Vec2 to Vector2
        self.position = pygame.math.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(150, 350)
        # Corrected from Vec2 to Vector2
        self.velocity = pygame.math.Vector2(speed * math.cos(angle), speed * math.sin(angle))
        self.lifetime = random.uniform(1, 2)
        self.elapsed_time = 0
        self.color = random.choice([RED, ORANGE, YELLOW, WHITE])

    def update(self, dt):
        self.position += self.velocity * dt
        self.velocity.y += GRAVITY * dt * 0.5
        self.elapsed_time += dt
        # Fade out effect
        if self.elapsed_time < self.lifetime:
            alpha = int(255 * (1 - self.elapsed_time / self.lifetime))
            self.color = (*self.color[:3], alpha)

    def draw(self, surface):
        if self.elapsed_time < self.lifetime:
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, self.color, (3, 3), 3)
            surface.blit(surf, (int(self.position.x) - 3, int(self.position.y) - 3))

class Fireworks:
    def __init__(self):
        self.particles = []
        self.active = False
        self.timer = 0
        self.duration = 2.5

    def start(self):
        self.active = True
        self.timer = 0
        self.create_firework()

    def create_firework(self):
        x = random.randint(200, WIDTH - 200)
        y = random.randint(100, HEIGHT // 2)
        for _ in range(60):
            self.particles.append(FireworkParticle(x, y))

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer > self.duration:
            self.active = False
            self.particles.clear()
        else:
            for particle in self.particles[:]:
                particle.update(dt)
                if particle.elapsed_time >= particle.lifetime:
                    self.particles.remove(particle)

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)