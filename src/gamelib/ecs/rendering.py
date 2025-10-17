from dataclasses import dataclass

from esper import Processor
import esper
import pygame

from gamelib.ecs.geometry import RectComponent


@dataclass
class RectSpriteComponent:
    surface: pygame.Surface
    rect: RectComponent
    color: tuple = (255, 255, 255)


class RenderRectProcessor(Processor):
    def process(self):
        for entity, draw_rect in esper.get_component(RectSpriteComponent):
            pygame.draw.rect(draw_rect.surface, draw_rect.color, draw_rect.rect.rect)
