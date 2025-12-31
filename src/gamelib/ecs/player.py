from dataclasses import dataclass

from esper import Processor
import esper
import pygame

from gamelib.ecs.geometry import PositionComponent


@dataclass
class PlayerControllerComponent:
    base_speed: int
    refractory_period: int
    last_space_time: int
    width: int
    height: int
    speed_multiplier: int = 1


class PlayerMoveProcessor(Processor):
    def process(self, dt):
        for entity, player in esper.get_component(PlayerControllerComponent):
            if not esper.has_component(entity, PositionComponent):
                continue
            pos = esper.component_for_entity(entity, PositionComponent)
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            if (
                keys[pygame.K_SPACE]
                and (current_time - player.last_space_time) > player.refractory_period
            ):
                player.base_speed = -player.base_speed
                player.last_space_time = current_time
            if pos.x < 0:
                pos.x = 0
                player.base_speed = abs(player.base_speed)
            elif pos.x > pygame.display.get_window_size()[0] - player.width:
                pos.x = pygame.display.get_window_size()[0] - player.width
                player.base_speed = -abs(player.base_speed)

            pos.x += player.base_speed
