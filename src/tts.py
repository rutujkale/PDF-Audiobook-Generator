import asyncio
import os
import subprocess

import edge_tts

from src.audio_merger import AudioMerger
from src.logger import get_logger
from src.utils import ensure_dir, rate_from_speed, split_into_chunks

log = get_logger(__name__)


class GenerationCancelled(Exception):
    """Raised when generation is cancelled mid-flight."""


def _ffmpeg_available():
    """True if the ``ffmpeg`` binary is runnable from Python."""

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class TextToSpeech:
    """Synthesize speech with edge-tts and merge the chunks into one MP3.

    Merging prefers an ffmpeg-based concat (fast, low memory) and falls
    back to pydub's :class:`AudioSegment` decoder when ffmpeg is missing.

    A ``cancel_check`` callable is polled between chunks; when it returns
    truthy, the run aborts, partial files are removed, and a
    :class:`GenerationCancelled` exception propagates to the caller.
    """

    def __init__(self, chunk_size=3500):
        self.chunk_size = chunk_size
        self._cancelled = False

    def cancel(self):
        """Request cancellation at the next chunk boundary."""

        self._cancelled = True

    async def _generate_chunk(self, text, voice, rate, filename):
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate
        )
        await communicate.save(filename)

    def create_audio(
        self,
        text,
        voice,
        speed,
        output_folder,
        progress_callback=None,
        cancel_check=None,
    ):
        """Generate ``Audiobook.mp3`` for ``text``.

        ``progress_callback`` receives ``(percent, message)`` where ``percent``
        spans 0–100 across synthesis + merge.
        """

        ensure_dir(output_folder)
        self._cancelled = False

        chunks = split_into_chunks(text, self.chunk_size)
        rate = rate_from_speed(speed)

        if not chunks:
            raise ValueError("No text to synthesize.")

        log.info(
            "Synthesizing %d chunks (%d chars) with voice=%s rate=%s",
            len(chunks), len(text), voice, rate
        )

        temp_files = []
        total = len(chunks)

        # --- Synthesis phase (0 -> 80%) -----------------------------
        for index, chunk in enumerate(chunks):

            if cancel_check and cancel_check():
                self._cleanup(temp_files)
                raise GenerationCancelled()

            filename = os.path.join(
                output_folder, f"part_{index + 1}.mp3"
            )

            try:
                asyncio.run(
                    self._generate_chunk(chunk, voice, rate, filename)
                )
            except Exception:
                if os.path.exists(filename):
                    os.remove(filename)
                raise

            temp_files.append(filename)

            if progress_callback:
                percent = int((index + 1) / total * 80)
                progress_callback(
                    percent,
                    f"Generated chunk {index + 1} of {total}"
                )

            log.debug("Chunk %d/%d done", index + 1, total)

        # --- Merge phase (80 -> 100%) -------------------------------
        final_path = os.path.join(output_folder, "Audiobook.mp3")

        if progress_callback:
            progress_callback(80, "Merging audio...")

        if _ffmpeg_available():
            log.info("Merging with ffmpeg concat")
            AudioMerger.merge(temp_files, final_path)
        else:
            log.info("ffmpeg unavailable, falling back to pydub merge")
            self._merge_with_pydub(temp_files, final_path)

        if progress_callback:
            progress_callback(95, "Finalizing...")

        # --- Cleanup parts -----------------------------------------
        self._cleanup(temp_files)

        if progress_callback:
            progress_callback(100, "Done")

        log.info("Audiobook written to %s", final_path)
        return final_path

    @staticmethod
    def _merge_with_pydub(audio_files, output_file):
        """In-process fallback merge used when ffmpeg is not installed."""

        from pydub import AudioSegment

        merged = AudioSegment.empty()
        for file in audio_files:
            merged += AudioSegment.from_mp3(file)

        merged.export(output_file, format="mp3")

    def _cleanup(self, files):
        for file in files:
            try:
                os.remove(file)
            except OSError as error:
                log.warning("Could not remove %s: %s", file, error)
