from typing import Tuple
from ecs.entity_manager import EntityManager
from ecs.entity import Entity
import pygame
from gamelib.ecs.geometry import PositionComponent, RectComponent
from gamelib.ecs.rendering import RectSpriteComponent
from gamelib.ecs.player import PlayerComponent

P_WIDTH = 50
P_HEIGHT = 50
WHITE = (255, 255, 255)


class PlayerSpawner:
    def __init__(self, entity_manager: EntityManager):
        self._entity_manager = entity_manager

    def spawn(self, position: Tuple[int, int], screen: pygame.Surface) -> Entity:
        new_player = self._entity_manager.create_entity()

        pos_component = PositionComponent(position[0], position[1])
        player_component = PlayerComponent(
            speed=5,
            refractory_period=300,
            last_space_time=0,
            width=P_WIDTH,
            height=P_HEIGHT,
        )
        rect_component = RectComponent(pos_component, P_WIDTH, P_HEIGHT)
        rect_sprite_component = RectSpriteComponent(screen, rect_component, WHITE)
        self._entity_manager.add_components(
            new_player,
            [
                pos_component,
                rect_component,
                rect_sprite_component,
                player_component,
            ],
        )
        return new_player
