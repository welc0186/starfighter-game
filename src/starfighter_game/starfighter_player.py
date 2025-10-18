from typing import Tuple
import esper
import pygame
from gamelib.ecs.collision import RectColliderComponent
from gamelib.ecs.custom import CustomProcessComponent
from gamelib.ecs.geometry import PositionComponent, RectComponent
from gamelib.ecs.rendering import RectSpriteComponent
from gamelib.ecs.player import PlayerControllerComponent
from starfighter_game.asteroid import AsteroidComponent

P_WIDTH = 50
P_HEIGHT = 50
WHITE = (255, 255, 255)


class StarfighterPlayerComponent(CustomProcessComponent):
    def __init__(self, rect_collider: RectColliderComponent) -> None:
        self.rect_collider = rect_collider
        self.game_over = False

    def process(self) -> None:
        if len(self.rect_collider.colliders) == 0:
            return
        for asteroid_entity, _ in esper.get_component(AsteroidComponent):
            asteroid_rect = esper.try_component(asteroid_entity, RectComponent)
            if asteroid_rect in self.rect_collider.colliders:
                self.game_over = True
                return


class PlayerSpawner:

    def spawn(self, position: Tuple[int, int], screen: pygame.Surface) -> int:
        pos_component = PositionComponent(position[0], position[1])
        player_component = PlayerControllerComponent(
            speed=5,
            refractory_period=300,
            last_space_time=0,
            width=P_WIDTH,
            height=P_HEIGHT,
        )
        rect_component = RectComponent(pos_component, P_WIDTH, P_HEIGHT)
        rect_sprite_component = RectSpriteComponent(screen, rect_component, WHITE)
        rect_collider_component = RectColliderComponent(rect_component)
        starfighter_player_component = StarfighterPlayerComponent(
            rect_collider_component
        )
        new_player = esper.create_entity(
            pos_component,
            rect_component,
            rect_sprite_component,
            player_component,
            rect_collider_component,
            starfighter_player_component,
        )
        return new_player
