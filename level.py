import pygame
from tile import Tile
from settings import *
import random

class Level:
    def __init__(self, message):
        self.tiles = []
        self.message = message
        self.generate_level()

    def generate_level(self):
        self.tiles = []
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

    def draw(self, surface):
        for tile in self.tiles:
            tile.draw(surface)