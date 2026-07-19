import os

import pygame

from src.logger import get_logger
from src.utils import format_duration

log = get_logger(__name__)

# pygame.mixer must be initialized exactly once. Track it so that repeated
# AudioPlayer() constructions do not re-init (which can crash on Windows).
_mixer_ready = False


def _ensure_mixer():
    global _mixer_ready

    if not _mixer_ready:
        pygame.mixer.init()
        _mixer_ready = True


class AudioPlayer:
    """Thin wrapper around ``pygame.mixer.music`` for audiobook playback.

    The mixer plays a single stream, which is exactly what we want.
    Pause/resume/stop map directly onto its primitives; position is
    polled via :meth:`get_position` and exposed for a UI time label.
    """

    def __init__(self, volume=0.8):
        _ensure_mixer()
        self.current_file = None
        self.is_paused = False
        self.is_playing = False
        self._start_offset = 0.0
        self._paused_at = 0.0
        self._volume = float(volume)
        pygame.mixer.music.set_volume(self._volume)

    # ----------------------------------------------------------------- #
    # Loading & transport
    # ----------------------------------------------------------------- #

    def play(self, filepath, start_pos=0.0):
        """Load ``filepath`` and begin playback from ``start_pos`` seconds."""

        if not filepath or not os.path.exists(filepath):
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        if self.is_playing:
            self.stop()

        pygame.mixer.music.load(filepath)
        if start_pos > 0:
            pygame.mixer.music.play(start=start_pos)
            self._start_offset = start_pos
        else:
            pygame.mixer.music.play()
            self._start_offset = 0.0

        pygame.mixer.music.set_volume(self._volume)

        self.current_file = filepath
        self.is_playing = True
        self.is_paused = False

        log.info("Playing %s", os.path.basename(filepath))

    def pause(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            log.debug("Playback paused at %s", format_duration(self.get_position()))

    def resume(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            log.debug("Playback resumed")

    def stop(self):
        if self.is_playing or self.is_paused:
            pygame.mixer.music.stop()

        pygame.mixer.music.unload()
        self.is_playing = False
        self.is_paused = False
        self._start_offset = 0.0

    # ----------------------------------------------------------------- #
    # State / queries
    # ----------------------------------------------------------------- #

    def set_volume(self, volume):
        """Set volume in the ``0.0``–``1.0`` range."""

        self._volume = max(0.0, min(1.0, float(volume)))
        pygame.mixer.music.set_volume(self._volume)

    def get_volume(self):
        return self._volume

    def get_position(self):
        """Current playback position in seconds, or ``None`` if idle.

        ``mixer.music.get_pos()`` returns ms since the last ``play()``;
        we add ``_start_offset`` so seeking forward works.
        """

        if not self.is_playing:
            return None

        if self.is_paused:
            return self._start_offset + (self._paused_at / 1000.0)

        raw = pygame.mixer.music.get_pos()

        if raw < 0:
            return None

        return self._start_offset + (raw / 1000.0)

    def seek(self, seconds):
        """Seek to an absolute position (seconds). Re-loads the file."""

        if not self.current_file:
            return

        was_paused = self.is_paused
        self.play(self.current_file, start_pos=max(0.0, float(seconds)))

        if was_paused:
            self.pause()

    def is_busy(self):
        return self.is_playing

    def is_finished(self):
        """True when playback ended naturally (track finished)."""

        return (
            not self.is_paused
            and not pygame.mixer.music.get_busy()
        )
