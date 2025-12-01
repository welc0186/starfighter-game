from dataclasses import dataclass

from esper import Processor
import esper
import pygame

from gamelib.ecs.geometry import PositionComponent


@dataclass
class RectSpriteComponent:
    surface: pygame.Surface
    rect: pygame.Rect
    color: tuple = (255, 255, 255)


class RenderRectProcessor(Processor):
    def process(self, dt):
        for entity, (position, rect_sprite) in esper.get_components(
            PositionComponent, RectSpriteComponent
        ):
            rect_sprite.rect.centerx = position.x
            rect_sprite.rect.centery = position.y

        for entity, draw_rect in esper.get_component(RectSpriteComponent):
            pygame.draw.rect(draw_rect.surface, draw_rect.color, draw_rect.rect)
