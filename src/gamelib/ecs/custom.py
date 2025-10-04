from abc import ABC, abstractmethod

from ecs.component import Component
from ecs.system import System


class CustomUpdateComponent(ABC, Component):
    @abstractmethod
    def update(self, dt: float) -> None:
        pass


class CustomUpdateSystem(System):
    def update(self, dt: float) -> None:
        for entity, custom_component in self.get_components(CustomUpdateComponent):
            custom_component.update(dt)
