from abc import ABC, abstractmethod

from esper import Processor
import esper


class CustomProcessComponent(ABC):
    @abstractmethod
    def process(self) -> None:
        pass


class CustomUpdateProcessor(Processor):
    def process(self) -> None:
        for entity, custom_component in esper.get_component(CustomProcessComponent):
            custom_component.process()
