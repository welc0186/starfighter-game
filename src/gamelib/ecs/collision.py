from dataclasses import dataclass

from ecs.component import Component
from ecs.system import System
from gamelib.ecs.geometry import RectComponent


@dataclass
class RectColliderComponent(Component):
    rect: RectComponent
    rect_colliders: list | None = None


class RectColliderSystem(System):
    def update(self, dt):
        for entity, collider in self.get_components(RectColliderComponent):
            collider.rect_colliders = []
            for other_entity, other_collider in self.get_components(
                RectColliderComponent
            ):
                if entity != other_entity and collider.rect.rect.colliderect(
                    other_collider.rect.rect
                ):
                    collider.rect_colliders.append(other_collider.rect)
