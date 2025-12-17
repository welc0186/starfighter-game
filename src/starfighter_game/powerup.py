from typing import Any
import esper
import pygame

from gamelib.ecs.geometry import PositionBoundsComponent
from gamelib.ecs.geometry import PositionComponent, VelocityComponent
from gamelib.ecs.collision import ColliderComponent
from gamelib.ecs.modifiers.modifier import add_modifier
from gamelib.ecs.modifiers.speed_modifier import SpeedModifier
from gamelib.ecs.rendering import RectSpriteComponent

SPU_W = 50
SPU_H = 50
SPU_SPEED = 5

YELLOW = (255, 255, 0)


class SpeedPowerUp:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, SPU_W, SPU_H)

    def on_collided(self, entity, other_entity, tags):
        if "player" in tags:
            add_modifier(other_entity, SpeedModifier())
            esper.delete_entity(entity)

    @property
    def components(self) -> list[Any]:
        return [
            PositionComponent(0, 0),
            PositionBoundsComponent(
                -50, 850, -50, 650, lambda e: esper.delete_entity(e)
            ),
            RectSpriteComponent(self.screen, self.rect, YELLOW),
            VelocityComponent((0, SPU_SPEED)),
            ColliderComponent(
                SPU_W,
                SPU_H,
                on_collision=self.on_collided,
                ignore_tags={"enemy", "projectile"},
            ),
        ]
