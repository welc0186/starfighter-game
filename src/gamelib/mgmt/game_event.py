from typing import Callable


class GameEvent:
    def __init__(self):
        self.listeners: list[Callable] = []

    def add_listener(self, listener: Callable):
        self.listeners.append(listener)

    def remove_listener(self, listener: Callable):
        self.listeners.remove(listener)

    def trigger(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)
