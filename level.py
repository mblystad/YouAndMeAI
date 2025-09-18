import pygame
from tile import Tile
from settings import *
import random

class Level:
    def __init__(self, message):
        self.tiles = []
        self.flowers = []
        self.message = message
        self.generate_level()

    def generate_level(self):
        self.tiles = []
        self.flowers = []
        # Ground layer
        for x in range(0, WIDTH, TILE_SIZE):
            self.tiles.append(Tile(x, HEIGHT - TILE_SIZE))
        # Random obstacles with gaps, start further to avoid player start
        num_obstacles = random.randint(2, 4)
        last_x = TILE_SIZE * 4  # Changed from TILE_SIZE * 2 to 200 to ensure clear start
        for _ in range(num_obstacles):
            obstacle_width = TILE_SIZE * random.randint(1, 3)
            gap = random.randint(TILE_SIZE * 2, TILE_SIZE * 4)
            obstacle_x = min(last_x + gap, WIDTH - obstacle_width - TILE_SIZE)
            obstacle_y = HEIGHT - TILE_SIZE * 2  # 1 tile high
            for x_pos in range(obstacle_x, obstacle_x + obstacle_width, TILE_SIZE):
                self.tiles.append(Tile(x_pos, obstacle_y))
            last_x = obstacle_x + obstacle_width

        # Gentle floating platforms for variation
        for _ in range(random.randint(1, 2)):
            platform_width = TILE_SIZE * random.randint(1, 2)
            platform_x = random.randint(TILE_SIZE * 4, WIDTH - TILE_SIZE * 4)
            platform_y = HEIGHT - TILE_SIZE * random.randint(3, 4)
            for x_pos in range(platform_x, platform_x + platform_width, TILE_SIZE):
                self.tiles.append(Tile(x_pos, platform_y))

        # Scatter flowers along the ground tiles
        ground_tiles = [tile for tile in self.tiles if tile.rect.bottom == HEIGHT]
        for tile in ground_tiles:
            if random.random() < 0.2:
                stem_height = random.randint(12, 18)
                flower_x = tile.rect.left + random.randint(10, TILE_SIZE - 10)
                flower_y = tile.rect.top - stem_height
                color = random.choice(FLOWER_COLORS)
                self.flowers.append({
                    "stem_start": (flower_x, tile.rect.top),
                    "stem_end": (flower_x, flower_y),
                    "color": color,
                    "radius": random.randint(4, 6),
                })

    def draw(self, surface):
        for tile in self.tiles:
            tile.draw(surface)
        for flower in self.flowers:
            pygame.draw.line(surface, GROUND_SHADOW, flower["stem_start"], flower["stem_end"], 2)
            pygame.draw.circle(surface, flower["color"], flower["stem_end"], flower["radius"])  # type: ignore[arg-type]
