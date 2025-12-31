from collections.abc import Callable

import esper


class TimerComponent:
    def __init__(self, duration_s: float, callback: Callable):
        self.duration_s = duration_s
        self.callback = callback
        self.elapsed_s = 0.0


class TimerProcessor(esper.Processor):
    def process(self, dt: float):
        for entity, timer in esper.get_component(TimerComponent):
            timer.elapsed_s += dt
            if timer.elapsed_s >= timer.duration_s:
                timer.callback()
                esper.remove_component(entity, TimerComponent)
