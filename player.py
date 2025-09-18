import pygame
from pygame.locals import *
from settings import *


class Player:
    def __init__(self, x, y):
        # Load player images
        stand_right = pygame.image.load("playerr.png").convert_alpha()
        jump_right = pygame.image.load("playerjr.png").convert_alpha()
        # Optional walk sprite (fallback to stand if missing)
        try:
            walk_right_raw = pygame.image.load("playersr.png").convert_alpha()
        except Exception:
            walk_right_raw = stand_right

        # Determine the maximum sprite size so animation frames align cleanly
        self.base_width = max(stand_right.get_width(), jump_right.get_width(), walk_right_raw.get_width())
        self.base_height = max(stand_right.get_height(), jump_right.get_height(), walk_right_raw.get_height())

        # Create oriented sprites with a shared anchor
        self.idle_right = self.center_image(stand_right)
        self.idle_left = pygame.transform.flip(self.idle_right, True, False)

        self.image_jump_right = self.center_image(jump_right)
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, True, False)

        walk_frame = self.center_image(walk_right_raw)
        self.walk_frames_right = [self.idle_right, walk_frame]
        self.walk_frames_left = [pygame.transform.flip(frame, True, False) for frame in self.walk_frames_right]
        self.walk_frame_index = 0
        self.walk_timer = 0.0
        self.walk_frame_duration = 0.22  # seconds per frame

        # Set initial image and rectangle
        self.image = self.idle_right
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))

        # Use floating-point positions for smoother movement
        self.pos_x = x
        self.pos_y = y

        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 300
        self.acceleration = 2500
        self.deceleration = 1800
        self.jump_height = 500
        self.on_ground = False
        self.facing_right = True
        self.controls_enabled = True
        self.moving_input = False

        # Jump forgiveness
        self.coyote_time = 0.12
        self.jump_buffer = 0.15
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.was_jump_pressed = False

        # Shadow
        self.shadow_surface = self._create_shadow_surface()

    def center_image(self, image):
        surface = pygame.Surface((self.base_width, self.base_height), pygame.SRCALPHA)
        rect = image.get_rect(center=(self.base_width // 2, self.base_height // 2))
        surface.blit(image, rect)
        return surface

    def set_controls_enabled(self, enabled: bool):
        self.controls_enabled = enabled

    def reset(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.walk_timer = 0.0
        self.walk_frame_index = 0
        self.facing_right = True
        self.image = self.idle_right
        self.moving_input = False
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()

        if not self.controls_enabled:
            self.vel_x = self._approach(self.vel_x, 0, self.deceleration * dt)
            self._update_jump_buffer(False)
            self.moving_input = False
            return

        direction = 0
        if keys[K_LEFT] or keys[K_a]:
            direction -= 1
        if keys[K_RIGHT] or keys[K_d]:
            direction += 1

        self.moving_input = direction != 0

        if direction != 0:
            self.vel_x += direction * self.acceleration * dt
            self.vel_x = max(-self.speed, min(self.vel_x, self.speed))
            self.facing_right = direction > 0
        else:
            self.vel_x = self._approach(self.vel_x, 0, self.deceleration * dt)

        jump_pressed = keys[K_SPACE] or keys[K_UP]
        self._update_jump_buffer(jump_pressed)

    def _update_jump_buffer(self, jump_pressed: bool):
        if jump_pressed and not self.was_jump_pressed:
            self.jump_buffer_timer = self.jump_buffer
        self.was_jump_pressed = jump_pressed

    def apply_physics(self, dt):
        # Gravity
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

    def move(self, tiles, dt):
        # Horizontal
        self.pos_x += self.vel_x * dt
        self.rect.x = int(self.pos_x)
        if self.rect.left < 0:
            self.pos_x = 0
            self.rect.left = 0
            self.vel_x = 0
        self.handle_collisions(tiles, "horizontal")

        # Vertical
        self.pos_y += self.vel_y * dt
        self.rect.y = int(self.pos_y)
        self.on_ground = False
        self.handle_collisions(tiles, "vertical")

        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def handle_collisions(self, tiles, direction):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if direction == "horizontal":
                    if self.vel_x > 0:  # right
                        self.pos_x = tile.rect.left - self.rect.width
                    elif self.vel_x < 0:  # left
                        self.pos_x = tile.rect.right
                    self.vel_x = 0
                elif direction == "vertical":
                    if self.vel_y > 0:  # falling
                        self.pos_y = tile.rect.top - self.rect.height
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # rising
                        self.pos_y = tile.rect.bottom
                        self.vel_y = 0
                self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def update_image(self, dt):
        is_walking = (
            self.on_ground
            and self.moving_input
            and abs(self.vel_x) > 28
            and self.controls_enabled
        )

        if is_walking:
            self.walk_timer += dt
            if self.walk_timer >= self.walk_frame_duration:
                self.walk_timer -= self.walk_frame_duration
                self.walk_frame_index = (self.walk_frame_index + 1) % len(self.walk_frames_right)
        else:
            self.walk_timer = 0.0
            self.walk_frame_index = 0

        if self.on_ground:
            frames = self.walk_frames_right if self.facing_right else self.walk_frames_left
            self.image = frames[self.walk_frame_index]
        else:
            self.image = self.image_jump_right if self.facing_right else self.image_jump_left

    def update(self, tiles, dt):
        self.update_timers(dt)
        self.handle_input(dt)
        self.try_jump()
        self.apply_physics(dt)
        self.move(tiles, dt)
        self.update_image(dt)

    def draw(self, surface):
        shadow_rect = self.shadow_surface.get_rect()
        shadow_rect.center = (self.rect.centerx, self.rect.bottom + 6)
        surface.blit(self.shadow_surface, shadow_rect)
        surface.blit(self.image, self.rect)

    def update_timers(self, dt):
        if self.on_ground:
            self.coyote_timer = self.coyote_time
        else:
            self.coyote_timer = max(0, self.coyote_timer - dt)

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer = max(0, self.jump_buffer_timer - dt)

    def try_jump(self):
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
            self.vel_y = -self.jump_height
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0

    def _approach(self, value, target, amount):
        if value < target:
            return min(target, value + amount)
        if value > target:
            return max(target, value - amount)
        return target

    def _create_shadow_surface(self):
        width = int(self.base_width * 0.7)
        height = 14
        shadow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect())
        return shadow
