import pygame
from tile import Tile
from settings import *
import random

class Level:
    BLUEPRINTS = [
        {
            "columns": [(6, 1, 1), (9, 2, 1), (13, 1, 1)],
            "platforms": [(4, 2, 3)],
        },
        {
            "columns": [(5, 1, 1), (7, 1, 1), (9, 1, 1), (12, 2, 1)],
            "platforms": [(8, 1, 4), (11, 1, 3)],
        },
        {
            "columns": [(6, 2, 1), (10, 1, 1), (14, 1, 1)],
            "platforms": [(7, 2, 3), (12, 1, 4)],
        },
        {
            "columns": [(4, 1, 1), (8, 2, 1), (11, 1, 1), (13, 1, 1)],
            "platforms": [(6, 1, 3), (9, 1, 4)],
        },
        {
            "columns": [(5, 1, 1), (7, 2, 1), (10, 1, 1), (12, 2, 1)],
            "platforms": [(6, 1, 3), (9, 2, 4)],
        },
        {
            "columns": [(6, 1, 1), (8, 1, 1), (10, 2, 1), (13, 1, 1)],
            "platforms": [(7, 1, 3), (11, 1, 4), (14, 1, 3)],
        },
    ]

    def __init__(self, index, message):
        self.index = index
        self.tiles = []
        self._tile_positions = set()  # Track occupied tile coords to avoid duplicates
        self.flowers = []
        self.message = message
        self.generate_level()

    def _add_tile(self, x, y):
        key = (x, y)
        if key not in self._tile_positions:
            self._tile_positions.add(key)
            self.tiles.append(Tile(x, y))

    def generate_level(self):
        self.tiles = []
        self.flowers = []
        self._tile_positions = set()

        # Base ground layer
        for x in range(0, WIDTH, TILE_SIZE):
            self._add_tile(x, HEIGHT - TILE_SIZE)

        blueprint = self.BLUEPRINTS[self.index % len(self.BLUEPRINTS)]

        # Nudge the layout slightly to keep things fresh while remaining fair
        lane_shift = min(self.index // len(self.BLUEPRINTS), 2)
        max_tile_index = WIDTH // TILE_SIZE

        def clamp_column_start(tile_x, width):
            return min(tile_x, max_tile_index - width - 1)

        # Place grounded columns (single-tile jumps and gentle doubles)
        for tile_x, width, height in blueprint.get("columns", []):
            start = clamp_column_start(tile_x + lane_shift, width)
            for dx in range(width):
                for level in range(height):
                    x_pos = (start + dx) * TILE_SIZE
                    y_pos = HEIGHT - TILE_SIZE * (2 + level)
                    self._add_tile(x_pos, y_pos)

        # Place floating platforms for optional shortcuts/rewards
        for tile_x, width, level_height in blueprint.get("platforms", []):
            start = clamp_column_start(tile_x + lane_shift, width)
            y_pos = HEIGHT - TILE_SIZE * level_height
            for dx in range(width):
                x_pos = (start + dx) * TILE_SIZE
                self._add_tile(x_pos, y_pos)

        # Deterministic RNG so levels feel curated per index
        rng = random.Random(self.index * 734)

        # Gentle floating platforms for variation (deterministic)
        num_extra = rng.randint(1, 2)
        max_tiles_wide = WIDTH // TILE_SIZE
        for _ in range(num_extra):
            platform_width_tiles = rng.randint(1, 2)
            start_tile_x = rng.randint(4, max(4, max_tiles_wide - (4 + platform_width_tiles)))
            platform_x = start_tile_x * TILE_SIZE
            platform_y = HEIGHT - TILE_SIZE * rng.randint(3, 4)
            for t in range(platform_width_tiles):
                self._add_tile(platform_x + t * TILE_SIZE, platform_y)

        # Scatter flowers along ground tiles (deterministic)
        ground_tiles = [tile for tile in self.tiles if tile.rect.bottom == HEIGHT]
        for tile in ground_tiles:
            if rng.random() < 0.22:
                stem_height = rng.randint(12, 18)
                flower_x = tile.rect.left + rng.randint(10, TILE_SIZE - 10)
                flower_y = tile.rect.top - stem_height
                color = rng.choice(FLOWER_COLORS)
                self.flowers.append({
                    "stem_start": (flower_x, tile.rect.top),
                    "stem_end": (flower_x, flower_y),
                    "color": color,
                    "radius": rng.randint(4, 6),
                })

    def draw(self, surface):
        for tile in self.tiles:
            tile.draw(surface)
        for flower in self.flowers:
            pygame.draw.line(surface, GROUND_SHADOW, flower["stem_start"], flower["stem_end"], 2)
            pygame.draw.circle(surface, flower["color"], flower["stem_end"], flower["radius"])  # type: ignore[arg-type]
