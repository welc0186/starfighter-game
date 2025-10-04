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

    def components_from_rect(self, rect: RectComponent) -> list[Component]:
        result = []
        if not self._is_entity_manager(self.entity_manager):
            return result
        entity = self.entity_manager.entity_for_component(rect)
        if entity is None:
            return result
        for component in self.entity_manager.components_for_entity(entity):
            if component is not rect:
                result.append(component)
        return result
