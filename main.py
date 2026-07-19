import sys

import ttkbootstrap as ttk

from src.gui import PDFAudioBookGUI
from src.logger import get_logger, setup_logging


def _install_excepthook():
    """Log uncaught exceptions instead of silently crashing."""

    log = get_logger(__name__)

    def handle(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return

        log.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_tb)
        )

    sys.excepthook = handle


def main():
    setup_logging()
    _install_excepthook()

    log = get_logger(__name__)
    log.info("Starting PDF Audiobook Generator")

    root = ttk.Window(themename="darkly")
    PDFAudioBookGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
