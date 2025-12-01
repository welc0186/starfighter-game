from abc import ABC, abstractmethod

from esper import Processor


from gamelib.ecs.utils import get_components_with_subclasses


class CustomProcessComponent(ABC):
    @abstractmethod
    def process(self) -> None:
        pass


class CustomUpdateProcessor(Processor):
    def process(self, dt) -> None:
        for entity, (custom_component,) in get_components_with_subclasses(
            CustomProcessComponent
        ):
            custom_component.process()
