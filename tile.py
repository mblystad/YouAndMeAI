import pygame
from settings import *

class Tile:
    def __init__(self, x, y):
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GROUND_GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)