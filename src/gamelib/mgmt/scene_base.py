from abc import ABC
from typing import Optional

import pygame


class SceneBase(ABC):
    def __init__(self, screen: pygame.Surface):
        self.next = self
        self.screen = screen

    def update(self, events, pressed_keys, dt: float = 0) -> None: ...

    def switch_to_scene(self, next_scene: Optional["SceneBase"]):
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)
