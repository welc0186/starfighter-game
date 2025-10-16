from dataclasses import dataclass
from typing import Iterator

from ecs.component import Component
from ecs.system import System
from gamelib.ecs.geometry import RectComponent


class RectColliderComponent(Component):
    def __init__(self, rect_component: RectComponent) -> None:
        self.rect_component = rect_component
        self.colliders: list[RectComponent] = []


class RectColliderSystem(System):
    def update(self, dt):
        for entity, collider in self.get_components(RectColliderComponent):
            collider.colliders = []
            for other_entity, rect_component in self.get_components(RectComponent):
                if entity != other_entity and collider.rect_component.rect.colliderect(
                    rect_component.rect
                ):
                    collider.colliders.append(rect_component)
