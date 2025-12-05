from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Tuple
import pygame
import random

from gamelib.ecs.collision import CollisionProcessor
from gamelib.ecs.custom import CustomUpdateProcessor
from gamelib.ecs.geometry import MoveProcessor, PositionComponent
from gamelib.ecs.modifiers.modifier import ModifierProcessor
from gamelib.ecs.player import PlayerMoveProcessor
from gamelib.ecs.rendering import RenderRectProcessor
import esper
from starfighter_game.asteroid import AsteroidSpawner
from starfighter_game.powerup import SpeedPowerUp
from starfighter_game.projectile import EntitySpawner, Projectile
from starfighter_game.starfighter_player import (
    PlayerSpawner,
    StarfighterPlayerComponent,
)

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Starfighter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Enemy settings
enemy_width = 50
enemies = []

# Bullet settings
bullet_width = 5
bullet_height = 10
bullets = []
bullet_speed = 7

# Power-up settings
powerup_radius = 20
powerup_speed = 2
powerups = []
powerup_active = False
powerup_duration = 5000  # milliseconds
powerup_start_time = 0


# Game loop control
clock = pygame.time.Clock()


def spawn_player(
    player_spawner: PlayerSpawner,
) -> Tuple[PositionComponent, StarfighterPlayerComponent]:
    player_entity = player_spawner.spawn((WIDTH // 2, HEIGHT - 60), screen)
    player_pos = esper.try_component(player_entity, PositionComponent)
    if player_pos is None:
        raise ValueError("Player position component not found")
    starfighter_player = esper.try_component(player_entity, StarfighterPlayerComponent)
    if starfighter_player is None:
        raise ValueError("StarfighterPlayerComponent not found")
    return player_pos, starfighter_player


async def main():
    score = 0
    running = True
    last_bullet_time = 0
    bullet_interval = 1000  # milliseconds
    powerup_active = False
    powerup_start_time: int = 0

    # ECS Setup
    esper.add_processor(PlayerMoveProcessor(), priority=99)
    esper.add_processor(MoveProcessor(), priority=98)
    esper.add_processor(CollisionProcessor(), priority=90)
    esper.add_processor(CustomUpdateProcessor(), priority=80)
    esper.add_processor(RenderRectProcessor())
    esper.add_processor(ModifierProcessor())

    asteroid_spawner = AsteroidSpawner(1000)
    player_spawner = PlayerSpawner()
    entity_spawner = EntitySpawner()

    player_pos, starfighter_player = spawn_player(player_spawner)

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()
        dt = clock.tick(60) / 1000.0

        esper.process(dt)

        # Spawn asteroids
        x = random.randint(0, WIDTH - enemy_width)
        asteroid_spawner.spawn(current_time, (x, 0), screen)

        # Fire a bullet every second
        if current_time - last_bullet_time > 1000:  # 1000 milliseconds = 1 second
            pojectile = entity_spawner.spawn(
                (player_pos.x, player_pos.y),
                Projectile(screen).components,
            )
            last_bullet_time = current_time

        # Spawn a power-up randomly
        if random.randint(1, 200) == 1:
            x = random.randint(powerup_radius, WIDTH - powerup_radius)
            entity_spawner.spawn((x, 0), SpeedPowerUp(screen).components)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))  # Draw score at the top-left corner

        if player_spawner.game_over:
            # Flash game over screen
            for _ in range(3):  # Flash 3 times
                screen.fill(RED)
                pygame.display.flip()
                await asyncio.sleep(0.5)
                screen.fill(BLACK)
                pygame.display.flip()
                await asyncio.sleep(0.5)
            # Restart the game
            esper.clear_database()
            player_spawner.game_over = False
            score = 0
            player_pos, starfighter_player = spawn_player(player_spawner)

        pygame.display.flip()
        # clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
