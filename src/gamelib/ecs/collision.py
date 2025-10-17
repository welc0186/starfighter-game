from dataclasses import dataclass
from typing import Iterator

from esper import Processor
import esper
from gamelib.ecs.geometry import RectComponent


class RectColliderComponent:
    def __init__(self, rect_component: RectComponent) -> None:
        self.rect_component = rect_component
        self.colliders: list[RectComponent] = []


class RectColliderProcessor(Processor):
    def process(self):
        for entity, collider in esper.get_component(RectColliderComponent):
            collider.colliders = []
            for other_entity, rect_component in esper.get_component(RectComponent):
                if entity != other_entity and collider.rect_component.rect.colliderect(
                    rect_component.rect
                ):
                    collider.colliders.append(rect_component)
