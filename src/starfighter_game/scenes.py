import random
import esper
from gamelib.mgmt.scene_base import SceneBase

from gamelib.ecs import (
    CollisionProcessor,
    CustomUpdateProcessor,
    MoveProcessor,
    PositionBoundsProcessor,
    RenderSurfaceProcessor,
    ModifierProcessor,
    PlayerMoveProcessor,
)
import pygame

from starfighter_game.asteroid import AsteroidSpawner
from starfighter_game.powerup import SpeedPowerUp
from starfighter_game.projectile import EntitySpawner, Projectile
from starfighter_game.starfighter_player import PlayerSpawner

ASTEROID_WIDTH = 50
POWERUP_RADIUS = 20


class MainScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        esper.switch_world("default")
        try:
            esper.delete_world("main")
        except KeyError:
            pass
        esper.switch_world("main")
        esper.clear_database()
        esper.add_processor(PlayerMoveProcessor(), priority=99)
        esper.add_processor(MoveProcessor(), priority=98)
        esper.add_processor(PositionBoundsProcessor(), priority=97)
        esper.add_processor(CollisionProcessor(), priority=90)
        esper.add_processor(CustomUpdateProcessor(), priority=80)
        esper.add_processor(RenderSurfaceProcessor(screen))
        esper.add_processor(ModifierProcessor())

        self.asteroid_spawner = AsteroidSpawner(1000)
        self.player_spawner = PlayerSpawner()
        self.entity_spawner = EntitySpawner()

        self.player_spawner.spawn(
            (screen.get_width() // 2, screen.get_height() - 60), screen
        )

        self.score = 0

        def add_score(points: int):
            self.score += points

        self.asteroid_spawner.destroyed_asteroid.connect(lambda entity: add_score(1))
        self.last_bullet_time = pygame.time.get_ticks()

    def update(self, events, pressed_keys, dt: float = 0) -> None:
        self.screen.fill((0, 0, 0))
        current_time = pygame.time.get_ticks()

        # Spawn asteroids
        x = random.randint(0, self.screen.get_width() - ASTEROID_WIDTH)
        self.asteroid_spawner.spawn(current_time, (x, 0))

        # Fire a bullet every second
        if current_time - self.last_bullet_time > 1000:  # 1000 milliseconds = 1 second
            pojectile = self.entity_spawner.spawn(
                (self.player_spawner.player_pos.x, self.player_spawner.player_pos.y),
                Projectile(self.screen).components,
            )
            self.last_bullet_time = current_time

        # Spawn a power-up randomly
        if random.randint(1, 200) == 1:
            x = random.randint(POWERUP_RADIUS, self.screen.get_width() - POWERUP_RADIUS)
            self.entity_spawner.spawn((x, 0), SpeedPowerUp(self.screen).components)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        esper.process(dt)

        if self.player_spawner.game_over:
            self.next = GameOverScene(self.screen, self.score)


class GameOverScene(SceneBase):
    def __init__(self, screen: pygame.Surface, final_score: int):
        super().__init__(screen)
        self.final_score = final_score

    def update(self, events, pressed_keys, dt: float = 0) -> None:
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        self.screen.blit(
            text, (self.screen.get_width() // 2 - text.get_width() // 2, 100)
        )

        font = pygame.font.Font(None, 36)
        score_text = font.render(
            f"Final Score: {self.final_score}", True, (255, 255, 255)
        )
        self.screen.blit(
            score_text,
            (self.screen.get_width() // 2 - score_text.get_width() // 2, 200),
        )

        if pressed_keys[pygame.K_RETURN]:
            self.next = MainScene(self.screen)
