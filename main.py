# /// script
# dependencies = [
#  "esper",
#  "psygnal",
#  "pygame",
# ]
# ///


import asyncio
import pygame

# pygbag requires importing in main.py
import esper
import psygnal

import sys

sys.path.append("./src")

from gamelib.mgmt.scene_base import SceneBase
from starfighter_game.scenes import GameOverScene, MainScene

# Screen dimensions
WIDTH, HEIGHT = 800, 600


async def run_game(fps: int, starting_scene: SceneBase):
    pygame.init()
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append(event)

        dt = clock.tick(fps) / 1000.0

        active_scene.update(filtered_events, pressed_keys, dt)

        active_scene = active_scene.next

        pygame.display.flip()
        await asyncio.sleep(0)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starfighter")
asyncio.run(run_game(60, MainScene(screen)))
