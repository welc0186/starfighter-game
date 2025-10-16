from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Tuple
import pygame
import random

from ecs.system import System
from ecs.system_manager import SystemManager

from ecs.entity import Entity
from ecs.entity_manager import EntityManager

from ecs.component import Component

from gamelib.ecs.collision import RectColliderSystem
from gamelib.ecs.custom import CustomUpdateSystem
from gamelib.ecs.geometry import MoveLinearSystem, PositionComponent
from gamelib.ecs.player import PlayerMoveSystem
from gamelib.ecs.rendering import RenderRectSystem
from starfighter_game.asteroid import AsteroidSpawner
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


def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)


def spawn_powerup():
    x = random.randint(powerup_radius, WIDTH - powerup_radius)
    new_powerup = pygame.Rect(x, 0, powerup_radius * 2, powerup_radius * 2)
    powerups.append(new_powerup)


def draw_powerups():
    for powerup in powerups:
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (powerup.x + powerup_radius, powerup.y + powerup_radius),
            powerup_radius,
        )


def spawn_player(
    player_spawner: PlayerSpawner, entity_manager: EntityManager
) -> Tuple[PositionComponent, StarfighterPlayerComponent]:
    player_entity = player_spawner.spawn((WIDTH // 2, HEIGHT - 60), screen)
    player_pos = entity_manager.get_component_safe(player_entity, PositionComponent)
    if player_pos is None:
        raise ValueError("Player position component not found")
    starfighter_player = entity_manager.get_component_safe(
        player_entity, StarfighterPlayerComponent
    )
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
    entity_manager = EntityManager()
    systems_manager = SystemManager(entity_manager)
    systems_manager.add_systems(
        [
            (PlayerMoveSystem(), 0),
            (MoveLinearSystem(), 0),
            (RectColliderSystem(), 20),
            (CustomUpdateSystem(), 80),
            (RenderRectSystem(), 99),
        ]
    )

    asteroid_spawner = AsteroidSpawner(1000, entity_manager)
    player_spawner = PlayerSpawner(entity_manager)
    entity_spawner = EntitySpawner(entity_manager)

    player_pos, starfighter_player = spawn_player(player_spawner, entity_manager)

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()

        systems_manager.update(0)

        # Spawn asteroids
        x = random.randint(0, WIDTH - enemy_width)
        asteroid_spawner.spawn(current_time, (x, 0), screen)

        # Fire a bullet every second
        if current_time - last_bullet_time > 1000:  # 1000 milliseconds = 1 second
            entity_spawner.spawn(
                (player_pos.x, player_pos.y),
                Projectile(screen).components,
            )
            last_bullet_time = current_time

        # Update bullets
        # for bullet in bullets:
        #     bullet.y -= bullet_speed
        #     if bullet.y < 0:
        #         bullets.remove(bullet)

        # Update power-ups
        if random.randint(1, 300) == 1:  # Spawn a power-up randomly
            spawn_powerup()
        for powerup in powerups[:]:
            powerup.y += powerup_speed
            if powerup.y > HEIGHT:
                powerups.remove(powerup)

        # Check for collisions between player and power-ups
        # player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        # for powerup in powerups[:]:
        #     if player_rect.colliderect(powerup):
        #         powerups.remove(powerup)
        #         powerup_active = True
        #         powerup_start_time = current_time

        # Handle power-up effect duration
        if powerup_active:
            bullet_interval = 500  # Fire bullets every 0.5 seconds
            if current_time - powerup_start_time > powerup_duration:
                powerup_active = False
                bullet_interval = 1000  # Reset to normal firing rate
        else:
            bullet_interval = 1000  # Normal firing rate

        # Fire a bullet based on current bullet_interval
        # if current_time - last_bullet_time > bullet_interval:
        #     bullet = pygame.Rect(
        #         player_x + player_width // 2 - bullet_width // 2,
        #         player_y,
        #         bullet_width,
        #         bullet_height,
        #     )
        #     bullets.append(bullet)
        #     last_bullet_time = current_time

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))  # Draw score at the top-left corner

        if starfighter_player.game_over:
            # Flash game over screen
            for _ in range(3):  # Flash 3 times
                screen.fill(RED)
                pygame.display.flip()
                await asyncio.sleep(0.5)
                screen.fill(BLACK)
                pygame.display.flip()
                await asyncio.sleep(0.5)
            # Restart the game
            entity_manager.clear()
            score = 0
            player_pos, starfighter_player = spawn_player(
                player_spawner, entity_manager
            )

        # draw_bullets()
        draw_powerups()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
