# Component Definitions
from typing import Tuple
from dataclasses import dataclass
from ecs.component import Component
from ecs.system import System
from ecs.entity_manager import EntityManager
import pygame


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


class MoveLinearSystem(System):
    def update(self, dt):
        for entity, speed_comp in self.get_components(MoveLinearComponent):
            pos = self.get_component_safe(entity, PositionComponent)
            if pos is None:
                return
            pos.x += speed_comp.speed[0]
            pos.y += speed_comp.speed[1]
