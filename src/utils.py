import os
import re

# Text cleaning is applied before sending chunks to the TTS engine.
# It removes common PDF artifacts (ligatures, headers/footers) that
# would otherwise be mispronounced or skipped by edge-tts.

_LIGATURES = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "st",
    "\ufb06": "st",
}

_HYPHEN_NEWLINE = re.compile(r"-\s*\n\s*")
_WHITESPACE = re.compile(r"\s+")


def sanitize_text(text):
    """Normalize extracted PDF text for TTS consumption.

    - Replace typographic ligatures with their ascii equivalents.
    - Rejoin words split across lines by a trailing hyphen.
    - Collapse any run of whitespace (spaces, tabs, newlines) into a
      single space — paragraph breaks are irrelevant for speech.
    """

    if not text:
        return ""

    for char, replacement in _LIGATURES.items():
        text = text.replace(char, replacement)

    text = _HYPHEN_NEWLINE.sub("", text)
    text = _WHITESPACE.sub(" ", text)

    return text.strip()


def split_into_chunks(text, chunk_size=3500):
    """Split ``text`` into <= ``chunk_size`` chunks on word boundaries.

    Falls back to a hard cut when no space is found within a chunk.
    """

    chunks = []

    if not text:
        return chunks

    text = text.replace("\n", " ").strip()

    while len(text) > chunk_size:

        split = text.rfind(" ", 0, chunk_size)

        if split == -1:
            split = chunk_size

        chunks.append(text[:split].strip())
        text = text[split:].strip()

    if text:
        chunks.append(text)

    return chunks


def format_duration(seconds):
    """Format a duration in seconds as ``H:MM:SS`` (or ``M:SS``)."""

    if seconds is None or seconds < 0:
        return "0:00"

    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"

    return f"{minutes}:{secs:02d}"


def human_size(num_bytes):
    """Human readable byte size."""

    if num_bytes is None or num_bytes < 0:
        return "0 B"

    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024

    return f"{num_bytes:.1f} TB"


def safe_filename(name, fallback="audiobook"):
    """Return a filesystem-safe base name (no extension)."""

    if not name:
        return fallback

    cleaned = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned[:120] or fallback


def ensure_dir(path):
    """Create ``path`` (and parents) if it does not exist."""

    if path:
        os.makedirs(path, exist_ok=True)

    return path


def rate_from_speed(speed):
    """Convert a 0.5–2.0 speed multiplier into an edge-tts ``rate`` string."""

    percent = int((float(speed) - 1.0) * 100)
    return f"{percent:+d}%"
