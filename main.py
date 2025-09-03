from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Tuple
import pygame
import random

from ecs.system import Component, System
from ecs.system_manager import SystemManager

from ecs.entity import Entity
from ecs.entity_manager import EntityManager

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

# Player settings
player_width = 50
player_height = 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

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


# Component Definitions
@dataclass
class PositionComponent(Component):
    x: int
    y: int


@dataclass
class MoveLinearComponent(Component):
    speed: Tuple[int, int]


@dataclass
class RectComponent(Component):
    pos: PositionComponent
    width: int
    height: int

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)


@dataclass
class RectSpriteComponent(Component):
    surface: pygame.Surface
    rect: RectComponent
    color: tuple = (255, 255, 255)


@dataclass
class RectColliderComponent(Component):
    rect: RectComponent
    rect_colliders: list | None = None


class RenderRectSystem(System):
    def update(self, dt):
        if self.entity_manager is None or not isinstance(
            self.entity_manager, EntityManager
        ):
            return
        for entity, draw_rect in self.entity_manager.pairs_for_type(
            RectSpriteComponent
        ):
            pygame.draw.rect(draw_rect.surface, draw_rect.color, draw_rect.rect)


class RectColliderSystem(System):
    def update(self, dt):
        if self.entity_manager is None or not isinstance(
            self.entity_manager, EntityManager
        ):
            return
        for entity, collider in self.entity_manager.pairs_for_type(
            RectColliderComponent
        ):
            collider.rect_colliders = []
            for other_entity, other_collider in self.entity_manager.pairs_for_type(
                RectColliderComponent
            ):
                if entity != other_entity and collider.rect.rect.colliderect(
                    other_collider.rect.rect
                ):
                    collider.rect_colliders.append(other_collider.rect)


class MoveLinearSystem(System):
    def update(self, dt):
        if self.entity_manager is None or not isinstance(
            self.entity_manager, EntityManager
        ):
            return
        for entity, speed_comp in self.entity_manager.pairs_for_type(
            MoveLinearComponent
        ):
            pos = self.entity_manager.component_for_entity(entity, PositionComponent)
            if pos is None:
                return
            pos.x += speed_comp.speed[0]
            pos.y += speed_comp.speed[1]


class Asteroid:
    def __init__(self, x: int, y: int, size: int = enemy_width, speed: int = 2):
        self.rect: pygame.Rect = pygame.Rect(x, y, size, size)
        self.speed: int = speed

    def move(self):
        self.rect.centery += self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


def spawn_enemy():
    while True:
        x = random.randint(0, WIDTH - enemy_width)
        new_enemy = Asteroid(x, 0)
        if not any(new_enemy.rect.colliderect(enemy) for enemy in enemies):
            enemies.append(new_enemy)
            break


def draw_player():
    pygame.draw.rect(screen, WHITE, (player_x, player_y, player_width, player_height))


def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)


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


async def main():
    global player_x, player_y
    score = 0
    running = True
    player_speed = 5
    last_space_time = 0
    last_bullet_time = 0
    bullet_interval = 1000  # milliseconds
    refractory_period = 300  # milliseconds
    powerup_active = False
    powerup_start_time: int = 0

    # ECS Setup
    entity_manager = EntityManager()
    systems_manager = SystemManager(entity_manager)
    systems_manager.add_system(RenderRectSystem(), priority=99)
    systems_manager.add_system(MoveLinearSystem(), priority=0)
    new_entity = entity_manager.create_entity()
    pos_component = PositionComponent(100, 100)
    rect_component = RectComponent(pos_component, 50, 50)
    entity_manager.add_component(new_entity, pos_component)
    entity_manager.add_component(new_entity, rect_component)
    entity_manager.add_component(
        new_entity, RectSpriteComponent(screen, rect_component, WHITE)
    )
    entity_manager.add_component(new_entity, MoveLinearComponent((0, 2)))

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()

        systems_manager.update(0)

        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_SPACE]
            and (current_time - last_space_time) > refractory_period
        ):
            player_speed = -player_speed  # Toggle direction
            last_space_time = current_time
        if player_x < 0:
            player_x = 0
            player_speed = abs(player_speed)
        elif player_x > WIDTH - player_width:
            player_x = WIDTH - player_width
            player_speed = -abs(player_speed)

        player_x += player_speed

        # Fire a bullet every second
        if current_time - last_bullet_time > 1000:  # 1000 milliseconds = 1 second
            bullet = pygame.Rect(
                player_x + player_width // 2 - bullet_width // 2,
                player_y,
                bullet_width,
                bullet_height,
            )
            bullets.append(bullet)
            last_bullet_time = current_time

        # Update enemies
        if random.randint(1, 50) == 1:  # Spawn an enemy randomly
            spawn_enemy()
        for enemy in enemies:
            enemy.move()
            if enemy.rect.y > HEIGHT:
                enemies.remove(enemy)

        # Update bullets
        for bullet in bullets:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)

        # Update power-ups
        if random.randint(1, 300) == 1:  # Spawn a power-up randomly
            spawn_powerup()
        for powerup in powerups[:]:
            powerup.y += powerup_speed
            if powerup.y > HEIGHT:
                powerups.remove(powerup)

        # Check for collisions between player and power-ups
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for powerup in powerups[:]:
            if player_rect.colliderect(powerup):
                powerups.remove(powerup)
                powerup_active = True
                powerup_start_time = current_time

        # Handle power-up effect duration
        if powerup_active:
            bullet_interval = 500  # Fire bullets every 0.5 seconds
            if current_time - powerup_start_time > powerup_duration:
                powerup_active = False
                bullet_interval = 1000  # Reset to normal firing rate
        else:
            bullet_interval = 1000  # Normal firing rate

        # Fire a bullet based on current bullet_interval
        if current_time - last_bullet_time > bullet_interval:
            bullet = pygame.Rect(
                player_x + player_width // 2 - bullet_width // 2,
                player_y,
                bullet_width,
                bullet_height,
            )
            bullets.append(bullet)
            last_bullet_time = current_time
        # Collision detection

        for bullet in bullets:
            for enemy in enemies:
                if bullet.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1  # Increment score
                    break

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))  # Draw score at the top-left corner

        # Check for collisions between enemies and player
        for enemy in enemies:
            if enemy.rect.colliderect(
                pygame.Rect(player_x, player_y, player_width, player_height)
            ):
                # Flash game over screen
                for _ in range(3):  # Flash 3 times
                    screen.fill(RED)
                    pygame.display.flip()
                    await asyncio.sleep(0.5)
                    screen.fill(BLACK)
                    pygame.display.flip()
                    await asyncio.sleep(0.5)
                # Restart the game
                enemies.clear()
                bullets.clear()
                score = 0
                player_x = WIDTH // 2 - player_width // 2
                player_y = HEIGHT - player_height - 10

        draw_player()
        draw_enemies()
        draw_bullets()
        draw_powerups()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
