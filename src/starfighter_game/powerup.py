from typing import Any
import pygame

from gamelib.ecs.geometry import PositionComponent, VelocityComponent
from gamelib.ecs.collision import ColliderComponent
from gamelib.ecs.rendering import RectSpriteComponent


SPU_W = 50
SPU_H = 50
SPU_SPEED = -5

YELLOW = (255, 255, 0)


class SpeedPowerUp:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, SPU_W, SPU_H)

    @property
    def components(self) -> list[Any]:
        return [
            PositionComponent(0, 0),
            RectSpriteComponent(self.screen, self.rect, YELLOW),
            VelocityComponent((0, SPU_SPEED)),
            ColliderComponent(
                SPU_W,
                SPU_H,
                tags={"projectile"},
                ignore_tags={"player"},
            ),
        ]
