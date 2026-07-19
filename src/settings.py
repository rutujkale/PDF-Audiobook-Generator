import json
import os

from src.logger import get_logger
from src.utils import ensure_dir

log = get_logger(__name__)

# Default settings used on first run and as a fallback for missing keys.
DEFAULTS = {
    "last_pdf_folder": "",
    "last_output_folder": "output",
    "voice": "en-US-GuyNeural",
    "speed": 1.0,
    "volume": 0.8,
    "chunk_size": 3500,
    "cleanup_parts": True,
}

# Where the JSON file lives. Kept next to the project so it is easy to find,
# but inside a user-level config dir on a real release build.
_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "settings.json")


class Settings:
    """JSON-backed persistent settings with sensible defaults."""

    def __init__(self, path=None):
        self.path = path if path is not None else _CONFIG_FILE
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        """Reload settings from disk, falling back to defaults."""

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                stored = json.load(file)

            # Only accept known keys; ignore unknown ones silently.
            for key in DEFAULTS:
                if key in stored:
                    self._data[key] = stored[key]

            log.debug("Loaded settings from %s", self.path)

        except FileNotFoundError:
            log.debug("Settings file not found, using defaults")

        except (json.JSONDecodeError, OSError) as error:
            log.warning("Could not read settings (%s), using defaults", error)

    def save(self):
        """Persist current settings to disk."""

        try:
            ensure_dir(os.path.dirname(self.path))

            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(self._data, file, indent=2)

            log.debug("Saved settings to %s", self.path)

        except OSError as error:
            log.error("Failed to save settings: %s", error)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def update(self, **values):
        """Update multiple keys at once (unknown keys are ignored)."""

        for key, value in values.items():
            if key in DEFAULTS:
                self._data[key] = value

    def as_dict(self):
        return dict(self._data)
