from os.path import join
from typing import Tuple
from psygnal import Signal
import pygame
import esper

from starfighter_game.game_events import ON_ASTEROID_DESTROYED

from gamelib.ecs import (
    ColliderComponent,
    VelocityComponent,
    PositionComponent,
    PositionBoundsComponent,
    RenderSurfaceComponent,
    TimerComponent,
)

RED = (255, 0, 0)
SCALE = 4
ASTEROID_W = 16 * SCALE
ASTEROID_H = 16 * SCALE

EXPLOSION_PATH = join("assets", "sounds", "small_explosion.wav")
SPRITE_PATH = join("assets", "images", "asteroid.png")
DESTROYED_SPRITE_PATH = join("assets", "images", "asteroid_destroyed.png")


class AsteroidSpawner:
    destroyed_asteroid = Signal(int)

    def __init__(self, spawn_interval: int):
        self._spawn_interval = spawn_interval
        self._last_spawn_time = 0
        # if not pygame.mixer.get_init():
        #     pygame.mixer.init()
        # self._sound = pygame.mixer.Sound(EXPLOSION_PATH)

    def spawn_destroyed_asteroid(self, position: Tuple[int, int]):
        # Play explosion sound
        # self._sound.play()
        entity = esper.create_entity(
            PositionComponent(position[0], position[1]),
            RenderSurfaceComponent.from_image(DESTROYED_SPRITE_PATH, True).scale(SCALE),
        )

        def destroy_entity(entity):
            if esper.has_component(entity, RenderSurfaceComponent):
                esper.delete_entity(entity)

        esper.add_component(entity, TimerComponent(0.2, lambda: destroy_entity(entity)))

    def on_asteroid_collided(self, entity, other_entity, tags):
        if "projectile" in tags:
            pos_comp = esper.component_for_entity(entity, PositionComponent)
            pos = pos_comp.x, pos_comp.y
            esper.delete_entity(entity)
            self.destroyed_asteroid.emit(entity)
            ON_ASTEROID_DESTROYED.trigger(entity)
            self.spawn_destroyed_asteroid(pos)
            # self._sound.play()

    def spawn(
        self,
        current_time: int,
        position: Tuple[int, int],
    ) -> None:
        if current_time - self._last_spawn_time < self._spawn_interval:
            return

        pos_component = PositionComponent(position[0], position[1])
        pos_bounds_component = PositionBoundsComponent(
            -50, 850, -50, 650, lambda e: esper.delete_entity(e)
        )
        surface_component = RenderSurfaceComponent.from_image(SPRITE_PATH, True).scale(
            SCALE
        )
        move_linear_component = VelocityComponent((0, 2))
        collider_component = ColliderComponent(
            ASTEROID_W,
            ASTEROID_H,
            tags={"enemy"},
            on_collision=self.on_asteroid_collided,
        )
        esper.create_entity(
            pos_component,
            pos_bounds_component,
            surface_component,
            move_linear_component,
            collider_component,
        )
        self._last_spawn_time = current_time
