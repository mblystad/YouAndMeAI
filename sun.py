import pygame
from settings import *

class Sun:
    def __init__(self):
        self.radius = SUN_RADIUS
        self.x = WIDTH - self.radius - 10
        self.start_y = SUN_START_Y
        self.end_y = SUN_END_Y
        self.current_y = self.start_y
        self.color = SUN_COLOR

    def update(self, level_progress):
        self.current_y = self.start_y + (self.end_y - self.start_y) * level_progress

    def draw(self, surface):
        glow_size = self.radius * 4
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_center = glow_surface.get_rect().center

        for i, alpha in enumerate((70, 45, 20)):
            scale = 2.6 - i * 0.7
            pygame.draw.circle(
                glow_surface,
                (*self.color, alpha),
                glow_center,
                int(self.radius * scale),
            )

        surface.blit(
            glow_surface,
            (int(self.x) - glow_center[0], int(self.current_y) - glow_center[1]),
        )
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.current_y)), self.radius)
