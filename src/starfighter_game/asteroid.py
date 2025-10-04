import random
from typing import Tuple
from ecs.entity import Entity
from ecs.entity_manager import EntityManager
from ecs.component import Component
import pygame

from gamelib.ecs.collision import RectColliderComponent
from gamelib.ecs.geometry import MoveLinearComponent, PositionComponent, RectComponent
from gamelib.ecs.rendering import RectSpriteComponent

RED = (255, 0, 0)


class AsteroidComponent(Component):
    pass


class AsteroidSpawner:
    def __init__(self, spawn_interval: int, entity_manager: EntityManager):
        self._spawn_interval = spawn_interval
        self._last_spawn_time = 0
        self._entity_manager = entity_manager

    def spawn(
        self, current_time: int, position: Tuple[int, int], screen: pygame.Surface
    ) -> None:
        if current_time - self._last_spawn_time < self._spawn_interval:
            return
        new_enemy = self._entity_manager.create_entity()
        pos_component = PositionComponent(position[0], position[1])
        rect_component = RectComponent(pos_component, 50, 50)
        rect_sprite_component = RectSpriteComponent(screen, rect_component, RED)
        move_linear_component = MoveLinearComponent((0, 2))
        asteroid_component = AsteroidComponent()
        self._entity_manager.add_components(
            new_enemy,
            [
                pos_component,
                rect_component,
                rect_sprite_component,
                move_linear_component,
                asteroid_component,
            ],
        )
        # enemies.append(new_enemy)
        self._last_spawn_time = current_time
