from os.path import join
from typing import Tuple
from psygnal import Signal
import pygame
import esper

from starfighter_game.game_events import ON_ASTEROID_DESTROYED

from gamelib.ecs.collision import ColliderComponent
from gamelib.ecs.geometry import (
    VelocityComponent,
    PositionComponent,
    PositionBoundsComponent,
)
from gamelib.ecs.rendering import RectSpriteComponent, RenderSurfaceComponent

RED = (255, 0, 0)
ASTEROID_W = 50
ASTEROID_H = 50

EXPLOSION_PATH = join("assets", "sounds", "small_explosion.wav")


class AsteroidSpawner:
    destroyed_asteroid = Signal(int)

    def __init__(self, spawn_interval: int):
        self._spawn_interval = spawn_interval
        self._last_spawn_time = 0
        # if not pygame.mixer.get_init():
        #     pygame.mixer.init()
        # self._sound = pygame.mixer.Sound(EXPLOSION_PATH)

    def on_asteroid_collided(self, entity, other_entity, tags):
        if "projectile" in tags:
            esper.delete_entity(entity)
            self.destroyed_asteroid.emit(entity)
            ON_ASTEROID_DESTROYED.trigger(entity)
            # self._sound.play()

    def spawn(
        self,
        current_time: int,
        position: Tuple[int, int],
    ) -> None:
        if current_time - self._last_spawn_time < self._spawn_interval:
            return

        pos_component = PositionComponent(position[0], position[1])
        pos_bounds_component = PositionBoundsComponent(
            -50, 850, -50, 650, lambda e: esper.delete_entity(e)
        )
        surface_component = RenderSurfaceComponent.solid_rect(
            ASTEROID_W, ASTEROID_H, RED
        )
        move_linear_component = VelocityComponent((0, 2))
        collider_component = ColliderComponent(
            ASTEROID_W,
            ASTEROID_H,
            tags={"enemy"},
            on_collision=self.on_asteroid_collided,
        )
        esper.create_entity(
            pos_component,
            pos_bounds_component,
            surface_component,
            move_linear_component,
            collider_component,
        )
        self._last_spawn_time = current_time
