# 📚 PDF Audiobook Generator

Convert any text-based PDF into a natural-sounding audiobook using Microsoft
Edge's neural TTS voices (`edge-tts`). Built with Python, `ttkbootstrap`, and
`pygame`.

## Features

- **Modern dark UI** built with `ttkbootstrap`
- **Chunked synthesis** — large PDFs are split into ≤3500-char chunks so they
  fit within edge-tts limits, then merged into a single `Audiobook.mp3`
- **Cancellable generation** — a Cancel button stops the run and cleans up
  partial files
- **Built-in player** — Play / Pause / Stop with live position readout and
  volume control
- **Persistent settings** — last voice, speed, volume, and folders are
  remembered across launches (`config/settings.json`)
- **PDF text cleanup** — rejoins hyphenated line breaks and normalizes
  ligatures before synthesis
- **File logging** — every run is logged under `logs/`

## Requirements

- Python 3.10+
- `ffmpeg` on your PATH (used by `pydub` for MP3 merge/export)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Click **Browse** next to *PDF* and pick a `.pdf` file.
2. (Optional) Choose a voice, adjust speed, and pick an output folder.
3. Click **Generate Audiobook**. Progress is shown in the bar and status line.
4. When generation finishes, the in-app **Player** becomes enabled — use
   ▶ / ⏹ to play and stop the result.

## Project layout

```
main.py                 # Entry point: logging + GUI bootstrap
src/
  __init__.py
  gui.py                # ttkbootstrap UI & event wiring
  worker.py             # Background generation thread (cancellable)
  pdf_reader.py         # PyMuPDF text extraction
  tts.py                # edge-tts synthesis + pydub merge
  audio_merger.py       # ffmpeg-based concat (alternative merger)
  player.py             # pygame.mixer playback wrapper
  settings.py           # JSON-backed persistent settings
  utils.py              # Text sanitization, time/size formatting, helpers
  logger.py             # Logging setup (console + file)
```

## Notes

- Scanned PDFs (image-only, no OCR text layer) will produce a "No readable
  text found" error — run them through an OCR tool first.
- Settings and logs are gitignored.
