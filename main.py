import pygame
import sys
import asyncio
from pygame.locals import *
from player import Player
from level import Level
from sun import Sun
from fireworks import Fireworks
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("You and Me")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 55, bold=True)  # For messages
game_font = pygame.freetype.Font(None, 36)       # For regular text
score_font = pygame.freetype.Font(None, 72)      # Fun, large font for score

def draw_background(screen, sun):
    top_color = SKY_BLUE
    bottom_color = DARK_BLUE
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    sun.draw(screen)

def display_message(screen, text, font, duration=2000):
    text_surface = font.render(text, True, BLACK)
    rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, rect)
    pygame.display.flip()
    pygame.time.delay(duration)

def display_score(screen, score, font):
    score_text = f"Score: {score}"
    font.render_to(screen, (10, 10), score_text, BLACK)

async def game_loop():
    player = Player(100, HEIGHT - TILE_SIZE * 2)
    sun = Sun()
    fireworks = Fireworks()
    levels = [Level(message=msg) for msg in MESSAGES]
    current_level_index = 0
    score = 0
    ask_for_points = False
    accepted_points = False
    show_score = False

    running = True
    while running:
        dt = min(clock.tick(FRAMERATE_LIMIT) / 1000.0, 0.1)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        current_level = levels[current_level_index]
        player.update(current_level.tiles, dt)

        # Check if player reaches the end of the level
        if player.rect.right >= WIDTH:
            fireworks.start()
            while fireworks.active and running:
                dt = min(clock.tick(FRAMERATE_LIMIT) / 1000.0, 0.1)
                fireworks.update(dt)
                draw_background(screen, sun)
                current_level.draw(screen)
                fireworks.draw(screen)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False

            if running:
                current_level_index += 1
                if current_level_index >= len(levels):
                    display_message(screen, "Thank you for playing!", font)
                    running = False
                else:
                    if current_level_index == len(levels) - 1:
                        ask_for_points = True  # Ask for points at the final level
                    player = Player(100, HEIGHT - TILE_SIZE * 2)

        # Handle points prompt
        if current_level_index == len(levels) - 1 and ask_for_points:
            screen.fill(DARK_BLUE)
            draw_background(screen, sun)
            current_level.draw(screen)
            player.draw(screen)
            game_font.render_to(screen, (100, 50), current_level.message, BLACK)
            display_message(screen, "Would you like points? Y/N", font, duration=0)  # No delay, wait for input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_y] and not accepted_points:
                accepted_points = True
                ask_for_points = False
                score += 1
                show_score = True
                display_message(screen, "Points accepted!", font)           # Show acceptance message
                display_message(screen, f"Score: {score}", score_font)      # Show score in fun font
            elif keys[pygame.K_n] and not accepted_points:
                accepted_points = False
                ask_for_points = False
                display_message(screen, "Points declined!", font)

        sun.update(current_level_index / len(levels))

        screen.fill(DARK_BLUE)
        draw_background(screen, sun)
        current_level.draw(screen)
        player.draw(screen)
        game_font.render_to(screen, (100, 50), current_level.message, BLACK)
        if show_score:
            display_score(screen, score, game_font)  # Regular score in top-left corner

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(game_loop())