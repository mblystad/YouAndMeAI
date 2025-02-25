import pygame
from pygame.locals import *
from settings import *


class Player:
    def __init__(self, x, y):
        # Load player images
        # Static standing images (right and left)
        self.image_right = pygame.image.load('playerr.png').convert_alpha()
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        # Jumping images (right and left)
        self.image_jump_right = pygame.image.load('playerjr.png').convert_alpha()
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, True, False)

        # Center all images to prevent visual jitter
        self.image_right = self.center_image(self.image_right)
        self.image_left = self.center_image(self.image_left)
        self.image_jump_right = self.center_image(self.image_jump_right)
        self.image_jump_left = self.center_image(self.image_jump_left)

        # Set initial image and rectangle
        self.image = self.image_right
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))

        # Use floating-point positions for smoother movement
        self.pos_x = x
        self.pos_y = y

        # Initialize physics variables
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 250
        self.jump_height = 450
        self.on_ground = False
        self.facing_right = True
        self.friction = 1000

    def center_image(self, image):
        # Find maximum dimensions among all images
        max_width = max(self.image_right.get_width(), self.image_jump_right.get_width())
        max_height = max(self.image_right.get_height(), self.image_jump_right.get_height())
        # Create a surface with transparency
        surface = pygame.Surface((max_width, max_height), pygame.SRCALPHA)
        # Center the image on the surface
        rect = image.get_rect(center=(max_width // 2, max_height // 2))
        surface.blit(image, rect)
        return surface

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        # Horizontal movement
        if keys[K_LEFT]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[K_RIGHT]:
            self.vel_x = self.speed
            self.facing_right = True
        # Jumping
        if keys[K_SPACE] and self.on_ground:
            self.vel_y = -self.jump_height
            self.on_ground = False

    def apply_physics(self, dt):
        # Apply gravity
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        # Apply friction when on ground
        if self.on_ground and self.vel_x != 0:
            friction_force = -self.vel_x / abs(self.vel_x) * self.friction * dt
            self.vel_x += friction_force
            if abs(self.vel_x) < 10:
                self.vel_x = 0

    def move(self, tiles, dt):
        # Horizontal movement using float positions
        self.pos_x += self.vel_x * dt
        self.rect.x = int(self.pos_x)
        # Keep player within screen bounds (left edge)
        if self.rect.left < 0:
            self.pos_x = 0
            self.rect.left = 0
            self.vel_x = 0
        self.handle_collisions(tiles, 'horizontal')

        # Vertical movement using float positions
        self.pos_y += self.vel_y * dt
        self.rect.y = int(self.pos_y)
        self.on_ground = False
        self.handle_collisions(tiles, 'vertical')

        # Update rect position based on float coordinates
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def handle_collisions(self, tiles, direction):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if direction == 'horizontal':
                    if self.vel_x > 0:  # Moving right
                        self.pos_x = tile.rect.left - self.rect.width
                    elif self.vel_x < 0:  # Moving left
                        self.pos_x = tile.rect.right
                    self.vel_x = 0
                elif direction == 'vertical':
                    if self.vel_y > 0:  # Falling down
                        self.pos_y = tile.rect.top - self.rect.height
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Moving up
                        self.pos_y = tile.rect.bottom
                        self.vel_y = 0
                # Update rect after adjusting position
                self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def update_image(self):
        # Select sprite based on ground state and facing direction
        if self.on_ground:
            # Use static image when on ground (no walking animation)
            self.image = self.image_right if self.facing_right else self.image_left
        else:
            # Use jumping animation when in the air
            self.image = self.image_jump_right if self.facing_right else self.image_jump_left

    def update(self, tiles, dt):
        self.handle_input()
        self.apply_physics(dt)
        self.move(tiles, dt)
        self.update_image()

    def draw(self, surface):
        surface.blit(self.image, self.rect)