# Component Definitions
from collections.abc import Callable
from typing import Any, Tuple
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


@dataclass
class PositionBoundsComponent:
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    on_out_of_bounds: Callable[[int], Any]


class MoveProcessor(Processor):
    def process(self, dt):
        for entity, (speed_comp, pos) in esper.get_components(
            VelocityComponent, PositionComponent
        ):
            # TO-DO: Factor for dt
            pos.x += speed_comp.base_speed[0]
            pos.y += speed_comp.base_speed[1]


class PositionBoundsProcessor(Processor):
    def process(self, dt):
        for entity, (pos, bounds) in esper.get_components(
            PositionComponent, PositionBoundsComponent
        ):
            if (
                pos.x < bounds.min_x
                or pos.x > bounds.max_x
                or pos.y < bounds.min_y
                or pos.y > bounds.max_y
            ):
                bounds.on_out_of_bounds(entity)
