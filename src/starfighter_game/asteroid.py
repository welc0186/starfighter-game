from typing import Tuple
from psygnal import Signal
import pygame
import esper

from gamelib.ecs.collision import ColliderComponent
from gamelib.ecs.geometry import (
    VelocityComponent,
    PositionComponent,
    PositionBoundsComponent,
)
from gamelib.ecs.rendering import RectSpriteComponent

RED = (255, 0, 0)
ASTEROID_W = 50
ASTEROID_H = 50


class AsteroidSpawner:
    destroyed_asteroid = Signal(int)

    def __init__(self, spawn_interval: int):
        self._spawn_interval = spawn_interval
        self._last_spawn_time = 0

    def on_asteroid_collided(self, entity, other_entity, tags):
        if "projectile" in tags:
            esper.delete_entity(entity)
            self.destroyed_asteroid.emit(entity)

    def spawn(
        self, current_time: int, position: Tuple[int, int], screen: pygame.Surface
    ) -> None:
        if current_time - self._last_spawn_time < self._spawn_interval:
            return

        pos_component = PositionComponent(position[0], position[1])
        pos_bounds_component = PositionBoundsComponent(
            -50, 850, -50, 650, lambda e: esper.delete_entity(e)
        )
        rect_sprite_component = RectSpriteComponent(
            screen, pygame.Rect(position[0], position[1], ASTEROID_W, ASTEROID_H), RED
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
            rect_sprite_component,
            move_linear_component,
            collider_component,
        )
        self._last_spawn_time = current_time
