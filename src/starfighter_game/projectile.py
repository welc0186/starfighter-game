from dataclasses import dataclass
from typing import Tuple
from ecs.component import Component
from ecs.system import System
from ecs.entity_manager import EntityManager
import pygame
from gamelib.ecs.geometry import MoveLinearComponent, PositionComponent, RectComponent
from gamelib.ecs.rendering import RectSpriteComponent


class ProjectileComponent(Component):
    pass


WHITE = (255, 255, 255)


class Projectile:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    @property
    def components(self) -> list[Component]:
        pos = PositionComponent(0, 0)
        rect = RectComponent(pos, 10, 10)
        return [
            pos,
            rect,
            ProjectileComponent(),
            RectSpriteComponent(self.screen, rect, WHITE),
            MoveLinearComponent((0, -5)),
        ]


class EntitySpawner:
    def __init__(self, entity_manager: EntityManager):
        self._entity_manager = entity_manager

    # TO-DO: Add necessary systems to system manager
    def spawn(self, position: Tuple[int, int], components: list[Component]) -> None:
        new_entity = self._entity_manager.create_entity()
        self._entity_manager.add_components(new_entity, components)
        pos = self._entity_manager.get_component_safe(new_entity, PositionComponent)
        if pos is None:
            pos = PositionComponent(position[0], position[1])
            self._entity_manager.add_component(new_entity, pos)
        pos.x = position[0]
        pos.y = position[1]
