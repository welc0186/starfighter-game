from dataclasses import dataclass
from ecs.component import Component
from ecs.system import System

import pygame

from gamelib.ecs.geometry import RectComponent


@dataclass
class RectSpriteComponent(Component):
    surface: pygame.Surface
    rect: RectComponent
    color: tuple = (255, 255, 255)


class RenderRectSystem(System):
    def update(self, dt):
        for entity, draw_rect in self.get_components(RectSpriteComponent):
            pygame.draw.rect(draw_rect.surface, draw_rect.color, draw_rect.rect.rect)
