from dataclasses import dataclass

from ecs.component import Component
from ecs.system import System
import pygame

from gamelib.ecs.geometry import PositionComponent


@dataclass
class PlayerComponent(Component):
    speed: int
    refractory_period: int
    last_space_time: int
    width: int
    height: int


class PlayerMoveSystem(System):
    def update(self, dt):
        for entity, player in self.get_components(PlayerComponent):
            pos = self.get_component_safe(entity, PositionComponent)
            if pos is None:
                return
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            if (
                keys[pygame.K_SPACE]
                and (current_time - player.last_space_time) > player.refractory_period
            ):
                player.speed = -player.speed
                player.last_space_time = current_time
            if pos.x < 0:
                pos.x = 0
                player.speed = abs(player.speed)
            elif pos.x > pygame.display.get_window_size()[0] - player.width:
                pos.x = pygame.display.get_window_size()[0] - player.width
                player.speed = -abs(player.speed)

            pos.x += player.speed
