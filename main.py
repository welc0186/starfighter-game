from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
from typing import Tuple, Optional, List
import pygame
import random

from ecs.system import System
from ecs.system_manager import SystemManager
from ecs.entity import Entity
from ecs.entity_manager import EntityManager
from ecs.component import Component

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
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)


# Component Definitions
@dataclass
class PositionComponent(Component):
    x: float
    y: float


@dataclass
class VelocityComponent(Component):
    vx: float
    vy: float


@dataclass
class SizeComponent(Component):
    width: float
    height: float


@dataclass
class CircleComponent(Component):
    radius: float


@dataclass
class ColorComponent(Component):
    color: Tuple[int, int, int]


@dataclass
class PlayerComponent(Component):
    speed: float = 5.0
    fire_rate: float = 1000.0  # milliseconds
    last_fire_time: float = 0.0
    direction: int = 1  # 1 for right, -1 for left
    last_space_time: float = 0.0


@dataclass
class EnemyComponent(Component):
    pass


@dataclass
class BulletComponent(Component):
    pass


@dataclass
class PowerUpComponent(Component):
    duration: float = 5000.0  # milliseconds
    fire_rate_multiplier: float = 0.5  # makes firing twice as fast


@dataclass
class CollisionComponent(Component):
    collided_entities: List[Entity] = field(default_factory=list)


@dataclass
class LifetimeComponent(Component):
    remaining_time: float


@dataclass
class GameStateComponent(Component):
    score: int = 0
    power_up_active: bool = False
    power_up_end_time: float = 0.0


# Custom Systems
class MovementSystem(System):
    def update(self, dt: float):
        for entity, vel in self.get_components(VelocityComponent):
            pos = self.get_component_safe(entity, PositionComponent)
            if pos:
                pos.x += vel.vx * dt
                pos.y += vel.vy * dt


class BoundarySystem(System):
    def update(self, dt: float):
        # Remove entities that are off-screen
        for entity, pos in self.get_components(PositionComponent):
            size = self.get_component_safe(entity, SizeComponent)
            circle = self.get_component_safe(entity, CircleComponent)

            # Check if entity is completely off screen
            if size:
                if (
                    pos.x < -size.width
                    or pos.x > WIDTH + size.width
                    or pos.y < -size.height
                    or pos.y > HEIGHT + size.height
                ):
                    self.remove_entity(entity)
            elif circle:
                if (
                    pos.x < -circle.radius * 2
                    or pos.x > WIDTH + circle.radius * 2
                    or pos.y < -circle.radius * 2
                    or pos.y > HEIGHT + circle.radius * 2
                ):
                    self.remove_entity(entity)


class PlayerControlSystem(System):
    def update(self, dt: float):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # for entity, (player, pos, size) in self.get_components(
        for entity, player in self.get_components(PlayerComponent):
            # Handle space key for direction change
            if keys[pygame.K_SPACE] and (current_time - player.last_space_time) > 300:
                player.direction *= -1
                player.last_space_time = current_time

            # Handle boundary collision and movement
            vel = self.get_component_safe(entity, VelocityComponent)
            pos = self.get_component_safe(entity, PositionComponent)
            size = self.get_component_safe(entity, SizeComponent)
            if not (vel and pos and size):
                return
            if pos.x <= 0:
                pos.x = 0
                player.direction = 1
            elif pos.x >= WIDTH - size.width:
                pos.x = WIDTH - size.width
                player.direction = -1

            vel.vx = player.speed * player.direction

            # Handle firing
            game_state = None
            for _, gs in self.get_components(GameStateComponent):
                game_state = gs
                break

            current_fire_rate = player.fire_rate
            if game_state and game_state.power_up_active:
                current_fire_rate *= 0.5  # Fire twice as fast with power-up

            if current_time - player.last_fire_time > current_fire_rate:
                self.create_bullet(pos.x + size.width / 2, pos.y)
                player.last_fire_time = current_time

    def create_bullet(self, x: float, y: float):
        # TO-DO: Handle entity manager checking better
        if not self._is_entity_manager(self.entity_manager):
            return
        bullet_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(bullet_entity, PositionComponent(x - 2.5, y))
        self.entity_manager.add_component(bullet_entity, VelocityComponent(0, -400))
        self.entity_manager.add_component(bullet_entity, SizeComponent(5, 10))
        self.entity_manager.add_component(bullet_entity, ColorComponent(WHITE))
        self.entity_manager.add_component(bullet_entity, BulletComponent())
        self.entity_manager.add_component(bullet_entity, CollisionComponent())


class EnemySpawnSystem(System):
    def __init__(self):
        super().__init__()
        self.spawn_timer = 0

    def update(self, dt: float):
        self.spawn_timer += dt
        if (
            self.spawn_timer > 0.02
        ):  # Spawn every 20ms (roughly 1/50 chance per frame at 60fps)
            if random.randint(1, 50) == 1:
                self.spawn_enemy()
            self.spawn_timer = 0

    def spawn_enemy(self):
        if not self._is_entity_manager(self.entity_manager):
            return
        x = random.randint(0, WIDTH - 50)
        enemy_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(enemy_entity, PositionComponent(x, 0))
        self.entity_manager.add_component(enemy_entity, VelocityComponent(0, 120))
        self.entity_manager.add_component(enemy_entity, SizeComponent(50, 50))
        self.entity_manager.add_component(enemy_entity, ColorComponent(RED))
        self.entity_manager.add_component(enemy_entity, EnemyComponent())
        self.entity_manager.add_component(enemy_entity, CollisionComponent())


class PowerUpSpawnSystem(System):
    def __init__(self):
        super().__init__()
        self.spawn_timer = 0

    def update(self, dt: float):
        self.spawn_timer += dt
        if self.spawn_timer > 0.02:  # Check every 20ms
            if random.randint(1, 300) == 1:
                self.spawn_powerup()
            self.spawn_timer = 0

    def spawn_powerup(self):
        if not self._is_entity_manager(self.entity_manager):
            return
        x = random.randint(20, WIDTH - 20)
        powerup_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(powerup_entity, PositionComponent(x, 0))
        self.entity_manager.add_component(powerup_entity, VelocityComponent(0, 120))
        self.entity_manager.add_component(powerup_entity, CircleComponent(20))
        self.entity_manager.add_component(powerup_entity, ColorComponent(YELLOW))
        self.entity_manager.add_component(powerup_entity, PowerUpComponent())
        self.entity_manager.add_component(powerup_entity, CollisionComponent())


class CollisionSystem(System):
    def update(self, dt: float):
        # Clear previous collisions
        for entity, collision in self.get_components(CollisionComponent):
            collision.collided_entities.clear()

        # Detect collisions
        collision_entities = list(self.get_components(CollisionComponent))

        for i, (entity1, collision1) in enumerate(collision_entities):
            for j, (entity2, collision2) in enumerate(
                collision_entities[i + 1 :], i + 1
            ):
                if self.check_collision(entity1, entity2):
                    collision1.collided_entities.append(entity2)
                    collision2.collided_entities.append(entity1)

    def check_collision(self, entity1: Entity, entity2: Entity) -> bool:
        pos1 = self.get_component_safe(entity1, PositionComponent)
        pos2 = self.get_component_safe(entity2, PositionComponent)

        if not pos1 or not pos2:
            return False

        # Rectangle collision
        size1 = self.get_component_safe(entity1, SizeComponent)
        size2 = self.get_component_safe(entity2, SizeComponent)
        circle1 = self.get_component_safe(entity1, CircleComponent)
        circle2 = self.get_component_safe(entity2, CircleComponent)

        # Rect vs Rect
        if size1 and size2:
            rect1 = pygame.Rect(pos1.x, pos1.y, size1.width, size1.height)
            rect2 = pygame.Rect(pos2.x, pos2.y, size2.width, size2.height)
            return rect1.colliderect(rect2)

        # Circle vs Rect
        elif circle1 and size2:
            circle_center = (pos1.x, pos1.y)
            rect = pygame.Rect(pos2.x, pos2.y, size2.width, size2.height)
            return self.circle_rect_collision(circle_center, circle1.radius, rect)

        # Rect vs Circle
        elif size1 and circle2:
            circle_center = (pos2.x, pos2.y)
            rect = pygame.Rect(pos1.x, pos1.y, size1.width, size1.height)
            return self.circle_rect_collision(circle_center, circle2.radius, rect)

        return False

    def circle_rect_collision(self, circle_center, radius, rect):
        closest_x = max(rect.left, min(circle_center[0], rect.right))
        closest_y = max(rect.top, min(circle_center[1], rect.bottom))
        distance_x = circle_center[0] - closest_x
        distance_y = circle_center[1] - closest_y
        return (distance_x**2 + distance_y**2) <= radius**2


class GameLogicSystem(System):
    def update(self, dt: float):
        current_time = pygame.time.get_ticks()

        # Get game state
        game_state = None
        for _, gs in self.get_components(GameStateComponent):
            game_state = gs
            break

        if not game_state:
            return

        # Check power-up expiration
        if game_state.power_up_active and current_time > game_state.power_up_end_time:
            game_state.power_up_active = False

        # Handle collisions
        for entity, collision in self.get_components(CollisionComponent):
            bullet_comp = self.get_component_safe(entity, BulletComponent)
            player_comp = self.get_component_safe(entity, PlayerComponent)
            powerup_comp = self.get_component_safe(entity, PowerUpComponent)
            enemy_comp = self.get_component_safe(entity, EnemyComponent)

            for collided_entity in collision.collided_entities:
                collided_bullet = self.get_component_safe(
                    collided_entity, BulletComponent
                )
                collided_player = self.get_component_safe(
                    collided_entity, PlayerComponent
                )
                collided_powerup = self.get_component_safe(
                    collided_entity, PowerUpComponent
                )
                collided_enemy = self.get_component_safe(
                    collided_entity, EnemyComponent
                )

                # Bullet hits enemy
                if bullet_comp and collided_enemy:
                    self.remove_entity(entity)
                    self.remove_entity(collided_entity)
                    game_state.score += 1

                # Enemy hits bullet
                elif enemy_comp and collided_bullet:
                    self.remove_entity(entity)
                    self.remove_entity(collided_entity)
                    game_state.score += 1

                # Player hits power-up
                elif player_comp and collided_powerup:
                    self.remove_entity(collided_entity)
                    game_state.power_up_active = True
                    game_state.power_up_end_time = current_time + 5000

                # Power-up hits player
                elif powerup_comp and collided_player:
                    self.remove_entity(entity)
                    game_state.power_up_active = True
                    game_state.power_up_end_time = current_time + 5000

                # Player hits enemy - Game Over
                elif player_comp and collided_enemy:
                    asyncio.create_task(self.game_over_sequence(game_state))

    async def game_over_sequence(self, game_state: GameStateComponent):
        # Flash screen
        for _ in range(3):
            screen.fill(RED)
            pygame.display.flip()
            await asyncio.sleep(0.5)
            screen.fill(BLACK)
            pygame.display.flip()
            await asyncio.sleep(0.5)

        # Reset game
        game_state.score = 0
        game_state.power_up_active = False
        game_state.power_up_end_time = 0

        # Clear all entities except player and game state
        entities_to_remove = []
        if not self._is_entity_manager(self.entity_manager):
            return
        for component_type in self.entity_manager.database:
            for entity in self.entity_manager.database[component_type].keys():
                if not self.get_component_safe(
                    entity, PlayerComponent
                ) and not self.get_component_safe(entity, GameStateComponent):
                    entities_to_remove.append(entity)

        for entity in entities_to_remove:
            self.remove_entity(entity)

        # Reset player position
        for entity, player in self.get_components(PlayerComponent):
            pos = self.get_component_safe(entity, PositionComponent)
            if pos:
                pos.x = WIDTH // 2 - 25
                pos.y = HEIGHT - 60
                player.direction = 1


class RenderSystem(System):
    def update(self, dt: float):
        screen.fill(BLACK)

        # Render rectangles
        # for entity, (pos, size, color) in self.get_components(
        for entity, size in self.get_components(SizeComponent):
            pos = self.get_component_safe(entity, PositionComponent)
            color = self.get_component_safe(entity, ColorComponent)
            if not (pos and color):
                continue
            rect = pygame.Rect(pos.x, pos.y, size.width, size.height)
            pygame.draw.rect(screen, color.color, rect)

        # Render circles
        for entity, circle in self.get_components(CircleComponent):
            pos = self.get_component_safe(entity, PositionComponent)
            color = self.get_component_safe(entity, ColorComponent)
            if not (pos and color):
                continue
            pygame.draw.circle(
                screen, color.color, (int(pos.x), int(pos.y)), int(circle.radius)
            )

        # Render UI
        for entity, game_state in self.get_components(GameStateComponent):
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {game_state.score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            if game_state.power_up_active:
                powerup_text = font.render("POWER UP ACTIVE!", True, GREEN)
                screen.blit(powerup_text, (10, 50))


async def main():
    clock = pygame.time.Clock()

    # ECS Setup
    entity_manager = EntityManager()
    system_manager = SystemManager(entity_manager)

    # Add systems in order of execution
    system_manager.add_system(PlayerControlSystem(), priority=1)
    system_manager.add_system(EnemySpawnSystem(), priority=2)
    system_manager.add_system(PowerUpSpawnSystem(), priority=3)
    system_manager.add_system(MovementSystem(), priority=4)
    system_manager.add_system(CollisionSystem(), priority=5)
    system_manager.add_system(GameLogicSystem(), priority=6)
    system_manager.add_system(BoundarySystem(), priority=7)
    system_manager.add_system(RenderSystem(), priority=99)

    # Create game state entity
    game_entity = entity_manager.create_entity()
    entity_manager.add_component(game_entity, GameStateComponent())

    # Create player entity
    player_entity = entity_manager.create_entity()
    entity_manager.add_component(
        player_entity, PositionComponent(WIDTH // 2 - 25, HEIGHT - 60)
    )
    entity_manager.add_component(player_entity, VelocityComponent(5, 0))
    entity_manager.add_component(player_entity, SizeComponent(50, 50))
    entity_manager.add_component(player_entity, ColorComponent(WHITE))
    entity_manager.add_component(player_entity, PlayerComponent())
    entity_manager.add_component(player_entity, CollisionComponent())

    running = True
    last_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        dt = current_time - last_time
        last_time = current_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update all systems
        system_manager.update(dt)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
