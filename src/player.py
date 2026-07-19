import pygame
import os


class AudioPlayer:

    def __init__(self):
        pygame.mixer.init()
        self.is_paused = False

    def load(self, file):

        if not os.path.exists(file):
            raise FileNotFoundError(file)

        pygame.mixer.music.load(file)

    def play(self):
        pygame.mixer.music.play()
        self.is_paused = False

    def pause(self):
        pygame.mixer.music.pause()
        self.is_paused = True

    def resume(self):
        pygame.mixer.music.unpause()
        self.is_paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_paused = False