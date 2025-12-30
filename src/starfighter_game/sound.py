from os.path import join
from gamelib.mgmt.game_mixer import GameMixer
import pygame

from starfighter_game.game_events import ON_ASTEROID_DESTROYED

EXPLOSION_PATH = join("assets", "sounds", "small_explosion.wav")


def init_sound() -> None:
    mixer = GameMixer()
    sound_explosion = pygame.mixer.Sound(EXPLOSION_PATH)
    ON_ASTEROID_DESTROYED.add_listener(lambda e: mixer.play_sound(sound_explosion))
