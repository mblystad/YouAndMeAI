import asyncio
import math
import random
import sys

import pygame
import pygame.freetype
from pygame.locals import *

from fireworks import Fireworks
from level import Level
from player import Player
from settings import *
from sun import Sun


LEVEL_COMPLETE_MESSAGES = [
    "Another clearing opens just for us.",
    "The sky blushes because we kept going.",
    "Every finish line feels softer beside you.",
]


class Cloud:
    def __init__(self):
        self.surface = None
        self.width = 0
        self.height = 0
        self.x = 0.0
        self.y = 0.0
        self.speed = 0.0
        self.reset(random.uniform(0, WIDTH))

    def reset(self, start_x: float):
        self.width = random.randint(140, 220)
        self.height = random.randint(60, 90)
        self.speed = random.uniform(15, 40)
        self.x = start_x
        self.y = random.randint(40, HEIGHT // 2)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        lumps = random.randint(3, 5)
        for _ in range(lumps):
            lump_width = random.randint(self.width // 3, self.width // 2)
            lump_height = random.randint(self.height // 2, self.height)
            rect = pygame.Rect(0, 0, lump_width, lump_height)
            rect.center = (
                random.randint(rect.width // 2, self.width - rect.width // 2),
                random.randint(rect.height // 2, self.height - rect.height // 2),
            )
            pygame.draw.ellipse(self.surface, (255, 255, 255, 180), rect)

    def update(self, dt: float):
        self.x += self.speed * dt
        if self.x - self.width > WIDTH:
            self.reset(-random.randint(80, 200))

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, (int(self.x), int(self.y)))


class Background:
    def __init__(self):
        self.day_surface = self._create_gradient(SKY_BLUE, HORIZON_BLUE)
        self.dusk_surface = self._create_gradient(TWILIGHT_TOP, TWILIGHT_BOTTOM)
        self.clouds = [Cloud() for _ in range(5)]

    def _create_gradient(self, top_color, bottom_color):
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
        return surface

    def update(self, dt: float):
        for cloud in self.clouds:
            cloud.update(dt)

    def draw(self, surface: pygame.Surface, progress: float):
        surface.blit(self.day_surface, (0, 0))
        dusk_alpha = max(0, min(255, int(200 * progress)))
        if dusk_alpha:
            self.dusk_surface.set_alpha(dusk_alpha)
            surface.blit(self.dusk_surface, (0, 0))
        for cloud in self.clouds:
            cloud.draw(surface)


class MessageOverlay:
    def __init__(self):
        self.text = None
        self.font = None
        self.color = WHITE
        self.duration = 0.0

    def show(self, text: str, duration: float | None, font: pygame.freetype.Font, color=WHITE):
        self.text = text
        self.font = font
        self.color = color
        self.duration = -1 if duration is None else duration

    def clear(self):
        self.text = None
               self.font = None
        self.duration = 0

    def update(self, dt: float):
        if self.text is None or self.duration == -1:
            return
        self.duration -= dt
        if self.duration <= 0:
            self.clear()

    def draw(self, surface: pygame.Surface):
        if not self.text or not self.font:
            return

        lines = self.text.split("\n")
        rendered = [self.font.render(line, self.color)[0] for line in lines]
        width = max(line.get_width() for line in rendered)
        height = sum(line.get_height() for line in rendered) + 8 * (len(rendered) - 1)

        panel = pygame.Surface((width + 40, height + 32), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 150), panel.get_rect(), border_radius=16)
        y = 16
        for line in rendered:
            x = (panel.get_width() - line.get_width()) // 2
            panel.blit(line, (x, y))
            y += line.get_height() + 8

        panel_rect = panel.get_rect(center=(WIDTH // 2, int(HEIGHT * 0.22)))
        surface.blit(panel, panel_rect)


class PointsPrompt:
    def __init__(self, message_font: pygame.freetype.Font, hint_font: pygame.freetype.Font):
        self.message_font = message_font
        self.hint_font = hint_font
        self.delay = -1.0
        self.active = False
        self.finished = False
        self.choice = None

    def activate(self, delay: float = 0.0):
        self.delay = max(0.0, delay)
        self.active = False
        self.finished = False
        self.choice = None

    def update(self, dt: float):
        if self.finished or self.delay < 0:
            return
        if not self.active:
            self.delay -= dt
            if self.delay <= 0:
                self.active = True

    def deactivate(self):
        self.delay = -1
        self.active = False
        self.finished = True
        self.choice = None

    def handle_event(self, event: pygame.event.Event):
        if not self.active or self.finished:
            return
        if event.type == KEYDOWN:
            if event.key == pygame.K_y:
                self.choice = True
                self.finished = True
            elif event.key == pygame.K_n:
                self.choice = False
                self.finished = True
        if self.finished:
            self.active = False
            self.delay = -1

    def consume_choice(self):
        choice = self.choice
        self.choice = None
        return choice

    def draw(self, surface: pygame.Surface):
        if not self.active or self.finished:
            return

        width = 500
        height = 140
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 160), panel.get_rect(), border_radius=18)

        main_text, _ = self.message_font.render("Would you like points?", WHITE)
        hint_text, _ = self.hint_font.render("Press Y to accept or N to keep walking.", (215, 225, 255))

        panel.blit(main_text, ((width - main_text.get_width()) // 2, 26))
        panel.blit(hint_text, ((width - hint_text.get_width()) // 2, 82))

        panel_rect = panel.get_rect(center=(WIDTH // 2, HEIGHT - 120))
        surface.blit(panel, panel_rect)


class GoalMarker:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - TILE_SIZE, HEIGHT - TILE_SIZE * 2, TILE_SIZE // 2, TILE_SIZE * 2 - 12)
        self.timer = 0.0

    def update(self, dt: float):
        self.timer += dt

    def draw(self, surface: pygame.Surface):
        glow_radius = int(28 + math.sin(self.timer * 4) * 6)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 255, 70), (glow_radius, glow_radius), glow_radius)
        glow_pos = (self.rect.centerx - glow_radius, self.rect.centery - glow_radius)
        surface.blit(glow_surface, glow_pos, special_flags=pygame.BLEND_PREMULTIPLIED)

        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=10)
        inner = self.rect.inflate(-6, -6)
        pygame.draw.rect(surface, (255, 215, 120), inner, border_radius=8)


def draw_story_panel(surface: pygame.Surface, font: pygame.freetype.Font, text: str):
    if not text:
        return
    text_surface, _ = font.render(text, (26, 33, 61))
    panel = pygame.Surface((text_surface.get_width() + 48, text_surface.get_height() + 32), pygame.SRCALPHA)
    pygame.draw.rect(panel, (255, 255, 255, 185), panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, (0, 0, 0, 25), panel.get_rect(), width=2, border_radius=16)
    panel.blit(text_surface, (24, 16))
    surface.blit(panel, (32, 40))


def draw_score(surface: pygame.Surface, font: pygame.freetype.Font, score: int):
    panel = pygame.Surface((170, 56), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 130), panel.get_rect(), border_radius=14)
    font.render_to(panel, (20, 18), f"Score: {score}", WHITE)
    surface.blit(panel, (24, 24))


async def game_loop():
    pygame.init()
    pygame.freetype.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("You and Me")
    clock = pygame.time.Clock()

    fonts = {
        "title": pygame.freetype.Font(None, 54),
        "story": pygame.freetype.Font(None, 30),
        "hud": pygame.freetype.Font(None, 28),
        "prompt": pygame.freetype.Font(None, 22),
    }

    background = Background()
    sun = Sun()
    fireworks = Fireworks()
    goal_marker = GoalMarker()

    # Build levels with index + message, matching Level(index, message)
    levels = [Level(index=i, message=msg) for i, msg in enumerate(MESSAGES)]
    current_level_index = 0
    current_level = levels[current_level_index]

    player = Player(100, HEIGHT - TILE_SIZE * 2)

    overlay = MessageOverlay()
    overlay.show(current_level.message, 4.0, fonts["story"], color=(36, 42, 68))

    points_prompt = PointsPrompt(fonts["story"], fonts["prompt"])
    score = 0
    level_transition = False
    end_sequence = False
    end_timer = 0.0

    running = True
    while running:
        dt = min(clock.tick(FRAMERATE_LIMIT) / 1000.0, 0.06)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

            points_prompt.handle_event(event)

        points_prompt.update(dt)
        overlay.update(dt)

        player.set_controls_enabled(not level_transition and not end_sequence)
        player.update(current_level.tiles, dt)

        fireworks.update(dt)

        if not level_transition and not end_sequence:
            if player.rect.centerx >= WIDTH - TILE_SIZE and player.vel_x >= 0:
                level_transition = True
                fireworks.start()
                player.vel_x = 0
                player.pos_x = min(player.pos_x, WIDTH - player.rect.width - 10)
                player.rect.x = int(player.pos_x)
                score += 100
                overlay.show(random.choice(LEVEL_COMPLETE_MESSAGES), 3.0, fonts["title"])

        if level_transition and not fireworks.active:
            current_level_index += 1
            if current_level_index >= len(levels):
                level_transition = False
                end_sequence = True
                end_timer = 5.0
                overlay.show("Thank you for staying until the twilight.", None, fonts["title"])
                points_prompt.deactivate()
            else:
                current_level = levels[current_level_index]
                player.reset(100, HEIGHT - TILE_SIZE * 2)
                level_transition = False
                overlay.show(current_level.message, 4.0, fonts["story"], color=(36, 42, 68))
                if current_level_index == len(levels) - 1:
                    points_prompt.activate(delay=2.5)

        choice = points_prompt.consume_choice()
        if choice is not None:
            if choice:
                score += 250
                overlay.show("I'll keep those points close.", 3.2, fonts["title"])
            else:
                overlay.show("The walk alone is worth more.", 3.2, fonts["story"], color=(36, 42, 68))

        if end_sequence:
            end_timer -= dt
            if end_timer <= 0:
                running = False

        progress = min((current_level_index + player.rect.centerx / WIDTH) / max(len(levels), 1), 1.0)
        background.update(dt)
        background.draw(screen, progress)
        sun.update(progress)
        sun.draw(screen)

        current_level.draw(screen)
        if not level_transition and not end_sequence:
            goal_marker.update(dt)
            goal_marker.draw(screen)

        player.draw(screen)
        fireworks.draw(screen)

        draw_story_panel(screen, fonts["story"], current_level.message)
        points_prompt.draw(screen)
        overlay.draw(screen)
        draw_score(screen, fonts["hud"], score)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(game_loop())
