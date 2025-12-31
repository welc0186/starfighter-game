import esper
from gamelib.ecs.geometry import VelocityComponent
from gamelib.ecs.modifiers.modifier import Modifier


class SpeedModifier(Modifier):
    """Increases entity speed by a multiplier"""

    def __init__(self, duration: float = 5.0, multiplier: float = 2):
        super().__init__("Speed Boost", duration)
        self.multiplier = multiplier
        self.original_multiplier = 1

    def on_apply(self, entity: int) -> None:
        if speed := esper.try_component(entity, VelocityComponent):
            self.original_multiplier = speed.multiplier
            speed.multiplier = self.multiplier

    def on_remove(self, entity: int) -> None:
        if speed := esper.try_component(entity, VelocityComponent):
            speed.multiplier = self.original_multiplier
