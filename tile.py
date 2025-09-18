import random
import pygame
from settings import *

class Tile:
    def __init__(self, x, y):
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self._build_tile_surface()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def _build_tile_surface(self):
        base_rect = self.image.get_rect()
        # Shadow base to give the tile depth
        pygame.draw.rect(self.image, GROUND_SHADOW, base_rect, border_radius=6)

        # Slight inset for the grassy top
        top_rect = base_rect.inflate(-6, -6)
        top_rect.height -= 6
        top_rect.y += 2
        pygame.draw.rect(self.image, GROUND_GREEN, top_rect, border_radius=6)

        # Soft highlight near the top edge
        highlight = pygame.Surface((top_rect.width, 8), pygame.SRCALPHA)
        highlight.fill((*WHITE, 45))
        self.image.blit(highlight, (top_rect.x, top_rect.y + 3))

        # Horizontal ridges for texture
        for offset in (top_rect.bottom - 12, top_rect.bottom - 20):
            pygame.draw.line(
                self.image,
                (*BLACK, 35),
                (top_rect.left + 6, offset),
                (top_rect.right - 6, offset),
                2,
            )

        # Add a few blades of grass with subtle variation
        for blade_x in range(top_rect.left + 6, top_rect.right - 6, 12):
            height = random.randint(6, 12)
            color_variation = min(255, GROUND_GREEN[1] + random.randint(0, 30))
            pygame.draw.line(
                self.image,
                (GROUND_GREEN[0], color_variation, GROUND_GREEN[2]),
                (blade_x, top_rect.top + 2),
                (blade_x + random.randint(-2, 2), top_rect.top - height),
                2,
            )
