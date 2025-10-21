from typing import Any, Tuple
import esper
import pygame
from gamelib.ecs.collision import ColliderComponent
from gamelib.ecs.geometry import VelocityComponent, PositionComponent
from gamelib.ecs.rendering import RectSpriteComponent


WHITE = (255, 255, 255)
PROJ_V = 5
PROJ_W = 10
PROJ_H = 10


def on_projectile_collided(entity, other_entity, tags):
    if "enemy" in tags:
        esper.delete_entity(entity)


class Projectile:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, PROJ_W, PROJ_H)

    @property
    def components(self) -> list[Any]:
        return [
            PositionComponent(0, 0),
            RectSpriteComponent(self.screen, self.rect, WHITE),
            VelocityComponent((0, -5)),
            ColliderComponent(
                PROJ_W,
                PROJ_H,
                tags={"projectile"},
                ignore_tags={"player"},
                on_collision=on_projectile_collided,
            ),
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
