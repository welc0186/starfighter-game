from typing import Any, Tuple
import esper
import pygame
from gamelib.ecs.geometry import VelocityComponent, PositionComponent, RectComponent
from gamelib.ecs.rendering import RectSpriteComponent


class ProjectileComponent:
    pass


WHITE = (255, 255, 255)


class Projectile:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    @property
    def components(self) -> list[Any]:
        pos = PositionComponent(0, 0)
        rect = RectComponent(pos, 10, 10)
        return [
            pos,
            rect,
            ProjectileComponent(),
            RectSpriteComponent(self.screen, rect, WHITE),
            VelocityComponent((0, 5)),
        ]
    
    def get_components(self) -> list[Any]:
        pos = PositionComponent(0,0)
        rect = RectComponent(pos, 10, 10)
        projectile = ProjectileComponent()
        rect_sprite = RectSpriteComponent(self.screen, rect, WHITE)
        veloctiy = VelocityComponent((0,-5))
        return [
            pos, rect, projectile, rect_sprite, veloctiy
        ]


class EntitySpawner:

    # TO-DO: Add necessary systems to system manager
    def spawn(self, position: Tuple[int, int], components: list[Any]) -> None:
        new_entity = esper.create_entity()
        # Can't specify components within create_entity() for some reason?
        for component in components:
            esper.add_component(new_entity, component)
        if esper.has_component(new_entity, PositionComponent):
            pos = esper.component_for_entity(new_entity, PositionComponent)
            pos.x = position[0]
            pos.y = position[1]
        else:
            esper.add_component(new_entity, PositionComponent(position[0], position[1]))
