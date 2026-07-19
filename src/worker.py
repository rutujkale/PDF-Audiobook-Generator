import threading

from src.logger import get_logger
from src.pdf_reader import PDFReader
from src.tts import TextToSpeech, GenerationCancelled
from src.utils import sanitize_text

log = get_logger(__name__)


class GenerationWorker:
    """Run audiobook generation on a background thread.

    Coordinates PDF extraction + TTS synthesis, reporting progress through
    callbacks and supporting cooperative cancellation via a threading.Event.

    The worker is single-shot: build a new instance per generation job.
    Callbacks are all invoked from the *worker* thread, so callers (the GUI)
    must marshal UI updates onto their own main thread.
    """

    # Progress milestones. TTS fills the 20–95 band proportionally.
    _PROGRESS_READ = 20
    _PROGRESS_TTS_START = 20
    _PROGRESS_TTS_END = 95
    _PROGRESS_DONE = 100

    def __init__(self, pdf_path, output_folder, voice, speed,
                 chunk_size=3500, cleanup_parts=True):
        self.pdf_path = pdf_path
        self.output_folder = output_folder
        self.voice = voice
        self.speed = speed
        self.chunk_size = chunk_size
        self.cleanup_parts = cleanup_parts

        self._cancel_event = threading.Event()
        self._thread = None
        self._tts = None

        # Callbacks invoked from the worker thread.
        self.on_progress = None      # (percent:int, message:str) -> None
        self.on_status = None        # (message:str) -> None
        self.on_finished = None      # (output_path:str) -> None
        self.on_cancelled = None     # () -> None
        self.on_error = None         # (error:Exception) -> None

    # ----------------------------------------------------------------- #
    # Lifecycle
    # ----------------------------------------------------------------- #

    def start(self):
        if self._thread and self._thread.is_alive():
            log.warning("Generation already running")
            return

        self._cancel_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        """Request cancellation. The worker checks the event between steps."""

        self._cancel_event.set()

        if self._tts:
            self._tts.cancel()

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    @property
    def is_cancelled(self):
        return self._cancel_event.is_set()

    # ----------------------------------------------------------------- #
    # Internal
    # ----------------------------------------------------------------- #

    def _emit_progress(self, percent, message=""):
        if self.on_progress:
            self.on_progress(percent, message)

    def _emit_status(self, message):
        if self.on_status:
            self.on_status(message)

    def _run(self):
        try:
            output = self._generate()

            if self.is_cancelled:
                log.info("Generation cancelled by user")
                if self.on_cancelled:
                    self.on_cancelled()
                return

            if self.on_finished:
                self.on_finished(output)

        except GenerationCancelled:
            log.info("Generation cancelled by user")
            if self.on_cancelled:
                self.on_cancelled()

        except Exception as error:
            log.exception("Generation failed")
            if self.on_error:
                self.on_error(error)

    def _generate(self):
        # --- Read PDF -------------------------------------------------
        self._emit_status("Reading PDF...")
        self._emit_progress(5, "Opening PDF")

        reader = PDFReader(self.pdf_path)
        reader.open()

        try:
            self._emit_progress(self._PROGRESS_READ // 2, "Extracting text")
            raw_text = reader.extract_text()
        finally:
            reader.close()

        if self.is_cancelled:
            return None

        text = sanitize_text(raw_text)

        if not text:
            raise ValueError(
                "No readable text found in this PDF. "
                "It may be a scanned document without an OCR text layer."
            )

        log.info(
            "Extracted %d chars from %s",
            len(text), self.pdf_path
        )

        self._emit_progress(self._PROGRESS_READ, "Text ready")

        # --- TTS ------------------------------------------------------
        self._emit_status("Generating audio...")
        self._tts = TextToSpeech(chunk_size=self.chunk_size)

        def tts_progress(percent, message=""):
            # Map TTS's 0-100 onto the wider 20-95 band so the read &
            # merge phases remain visible in the bar.
            scaled = self._PROGRESS_TTS_START + int(
                (percent / 100.0)
                * (self._PROGRESS_TTS_END - self._PROGRESS_TTS_START)
            )
            self._emit_progress(scaled, message)

        self._emit_progress(self._PROGRESS_TTS_START, "Synthesizing speech")

        output = self._tts.create_audio(
            text=text,
            voice=self.voice,
            speed=self.speed,
            output_folder=self.output_folder,
            progress_callback=tts_progress,
            cancel_check=self._cancel_event.is_set,
        )

        if self.is_cancelled:
            return None

        self._emit_progress(self._PROGRESS_DONE, "Done")
        return output
