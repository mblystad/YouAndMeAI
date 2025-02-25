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
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.current_y)), self.radius)