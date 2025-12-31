from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import esper


@dataclass
class ProbeComponent:
    component: object
    callable: Callable


class ProbeProcessor(esper.Processor):
    def process(self, dt) -> None:
        for entity, probe in esper.get_component(ProbeComponent):
            probe.callable(entity, probe.component)
