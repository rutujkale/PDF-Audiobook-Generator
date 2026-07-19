import logging
import os
from datetime import datetime

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def setup_logging(level=logging.INFO, log_dir="logs"):
    """Configure root logging once.

    Writes to the console and to a timestamped file inside ``log_dir``.
    Safe to call multiple times — only the first call has an effect.
    """

    global _initialized

    if _initialized:
        return

    os.makedirs(log_dir, exist_ok=True)

    filename = os.path.join(
        log_dir,
        f"audiobook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)

    root = logging.getLogger()
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = logging.FileHandler(filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _initialized = True


def get_logger(name):
    """Return a module-level logger."""

    return logging.getLogger(name)
