from dataclasses import dataclass
from typing import Self

from esper import Processor
import esper
import pygame
from pygame import Surface

from gamelib.ecs.geometry import PositionComponent


class RenderSurfaceComponent:
    def __init__(self, surface: Surface):
        self.surface = surface

    @classmethod
    def from_rect(cls, rect: pygame.Rect, color: tuple = (255, 255, 255)):
        surface = Surface((rect.width, rect.height))
        surface.fill(color)
        return cls(surface)

    @classmethod
    def solid_rect(cls, width: int, height: int, color: tuple = (255, 255, 255)):
        surface = Surface((width, height))
        surface.fill(color)
        return cls(surface)

    @classmethod
    def from_image(cls, image_path: str, transparent_pixels: bool = False):
        image = pygame.image.load(image_path)
        if transparent_pixels:
            image = image.convert_alpha()
            return cls(image)
        image = image.convert()
        return cls(image)

    def scale(self, factor: float) -> Self:
        new_size = (
            int(self.surface.get_width() * factor),
            int(self.surface.get_height() * factor),
        )
        self.surface = pygame.transform.scale(self.surface, new_size)
        return self


@dataclass
class RectSpriteComponent:
    surface: Surface
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


class RenderSurfaceProcessor(Processor):
    def __init__(self, screen: Surface):
        super().__init__()
        self.screen = screen

    def process(self, dt):
        for entity, (position, surface) in esper.get_components(
            PositionComponent, RenderSurfaceComponent
        ):
            self.screen.blit(surface.surface, (position.x, position.y))
