from os.path import join
from gamelib.mgmt.game_mixer import GameMixer
import pygame

from starfighter_game.game_events import *

EXPLOSION_PATH = join("assets", "sounds", "small_explosion.wav")
PROJECTILE_LAUNCH_PATH = join("assets", "sounds", "blipSelect_0002.wav")


def init_sound() -> None:
    mixer = GameMixer()
    sound_explosion = pygame.mixer.Sound(EXPLOSION_PATH)
    sound_projectile = pygame.mixer.Sound(PROJECTILE_LAUNCH_PATH)
    sound_projectile.set_volume(0.2)
    ON_ASTEROID_DESTROYED.add_listener(lambda e: mixer.play_sound(sound_explosion))
    ON_PROJECTILE_LAUNCHED.add_listener(lambda: mixer.play_sound(sound_projectile))
