# Component Definitions
from typing import Tuple
from dataclasses import dataclass
from esper import Processor
import esper
import pygame


@dataclass
class PositionComponent:
    x: int
    y: int


@dataclass
class VelocityComponent:
    base_speed: Tuple[int, int]
    multiplier: float = 1


@dataclass
class RectComponent:
    pos: PositionComponent
    width: int
    height: int

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)


class MoveProcessor(Processor):
    def process(self, dt):
        for entity, speed_comp in esper.get_component(VelocityComponent):
            pos = esper.try_component(entity, PositionComponent)
            if pos:
                # TO-DO: Factor for dt
                pos.x += speed_comp.base_speed[0]
                pos.y += speed_comp.base_speed[1]
