from typing import Callable, Set, Tuple
import esper
import pygame
from gamelib.ecs.collision import ColliderComponent
from gamelib.ecs.geometry import PositionComponent, RectComponent
from gamelib.ecs.rendering import RenderSurfaceComponent
from gamelib.ecs.player import PlayerControllerComponent

P_WIDTH = 50
P_HEIGHT = 50
WHITE = (255, 255, 255)


class StarfighterPlayerComponent:
    def __init__(self) -> None:
        self.game_over = False


class PlayerSpawner:

    def __init__(self) -> None:
        self.game_over = False
        self.player_pos = PositionComponent(-100, -100)

    def on_player_collided(self, entity: int, other_entity: int, tags: Set[str]):
        if "enemy" in tags:
            self.game_over = True

    def spawn(self, position: Tuple[int, int], screen: pygame.Surface) -> int:
        self.player_pos = PositionComponent(position[0], position[1])
        player_component = PlayerControllerComponent(
            base_speed=5,
            refractory_period=300,
            last_space_time=0,
            width=P_WIDTH,
            height=P_HEIGHT,
        )
        surface_component = RenderSurfaceComponent.solid_rect(P_WIDTH, P_HEIGHT, WHITE)
        starfighter_player_component = StarfighterPlayerComponent()
        rect_collider_component = ColliderComponent(
            P_WIDTH,
            P_HEIGHT,
            tags={"player"},
            ignore_tags={"projectile"},
            on_collision=self.on_player_collided,
        )
        new_player = esper.create_entity(
            self.player_pos,
            surface_component,
            player_component,
            rect_collider_component,
            starfighter_player_component,
        )
        return new_player
