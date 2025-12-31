import pygame


class GameMixer:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.channels: list[pygame.mixer.Channel] = []
        for i in range(pygame.mixer.get_num_channels()):
            self.channels.append(pygame.mixer.Channel(i))

    def play_sound(self, sound: pygame.mixer.Sound):
        for channel in self.channels:
            if not channel.get_busy():
                channel.play(sound)
                return
