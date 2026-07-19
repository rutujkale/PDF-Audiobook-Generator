import os
import threading

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox

from src.logger import get_logger
from src.player import AudioPlayer
from src.settings import Settings
from src.utils import format_duration
from src.worker import GenerationWorker, GenerationCancelled

log = get_logger(__name__)

VOICES = [
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
]

# How often (ms) the player position label refreshes during playback.
_POSITION_POLL_MS = 250


class PDFAudioBookGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("PDF Audiobook Generator")

        self.root.geometry("1000x720")
        self.root.minsize(900, 680)

        self.settings = Settings()
        self.player = AudioPlayer(volume=self.settings.get("volume", 0.8))

        self.pdf_path = ""
        self.output_folder = self.settings.get("last_output_folder") or "output"
        self.last_audio_path = ""

        self.worker = None

        self.create_widgets()
        self.apply_settings_to_widgets()
        self.poll_player()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):

        # ===========================
        # Header
        # ===========================

        title = ttk.Label(
            self.root,
            text="📚 PDF Audiobook Generator",
            font=("Segoe UI", 24, "bold")
        )

        title.pack(pady=(20, 5))

        subtitle = ttk.Label(
            self.root,
            text="Convert any PDF into a natural sounding audiobook",
            font=("Segoe UI", 11)
        )

        subtitle.pack()

        ttk.Separator(self.root).pack(fill="x", padx=20, pady=20)

        # ===========================
        # Main Frame
        # ===========================

        main_frame = ttk.Frame(self.root)

        main_frame.pack(fill="both", expand=True, padx=20)

        # ===========================
        # PDF Section
        # ===========================

        pdf_frame = ttk.LabelFrame(
            main_frame,
            text=" PDF "
        )

        pdf_frame.pack(fill="x", pady=10)

        self.file_label = ttk.Label(
            pdf_frame,
            text="No PDF Selected",
            width=70
        )

        self.file_label.pack(
            side="left",
            padx=15,
            pady=15
        )

        ttk.Button(
            pdf_frame,
            text="Browse",
            bootstyle="primary",
            command=self.select_pdf
        ).pack(
            side="right",
            padx=15
        )

        # ===========================
        # Voice Section
        # ===========================

        voice_frame = ttk.LabelFrame(
            main_frame,
            text=" Voice Settings "
        )

        voice_frame.pack(fill="x", pady=10)

        ttk.Label(
            voice_frame,
            text="Voice"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=15
        )

        self.voice = ttk.Combobox(
            voice_frame,
            values=VOICES,
            width=30
        )

        self.voice.current(0)

        self.voice.grid(
            row=0,
            column=1,
            padx=10
        )

        ttk.Label(
            voice_frame,
            text="Speed"
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        self.speed = ttk.Scale(
            voice_frame,
            from_=0.5,
            to=2.0,
            orient="horizontal",
            length=180,
            command=self.on_speed_change
        )

        self.speed.set(1.0)

        self.speed.grid(
            row=0,
            column=3,
            padx=10
        )

        self.speed_value = ttk.Label(
            voice_frame,
            text="1.0x",
            width=5
        )

        self.speed_value.grid(
            row=0,
            column=4,
            padx=(0, 10)
        )

        # ===========================
        # Output Folder
        # ===========================

        output_frame = ttk.LabelFrame(
            main_frame,
            text=" Output "
        )

        output_frame.pack(fill="x", pady=10)

        self.output_label = ttk.Label(
            output_frame,
            text=self.output_folder,
            width=70
        )

        self.output_label.pack(
            side="left",
            padx=15,
            pady=15
        )

        ttk.Button(
            output_frame,
            text="Browse",
            bootstyle="info",
            command=self.select_output_folder
        ).pack(
            side="right",
            padx=15
        )

        # ===========================
        # Progress
        # ===========================

        progress_frame = ttk.Frame(main_frame)

        progress_frame.pack(fill="x", pady=20)

        self.progress = ttk.Progressbar(
            progress_frame,
            length=700,
            mode="determinate",
            bootstyle="success-striped"
        )

        self.progress.pack()

        # ===========================
        # Generate / Cancel Buttons
        # ===========================

        button_frame = ttk.Frame(main_frame)

        button_frame.pack(pady=10)

        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate Audiobook",
            bootstyle="success",
            width=25,
            command=self.start_generation
        )

        self.generate_btn.grid(row=0, column=0, padx=10)

        self.cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="danger",
            width=15,
            command=self.cancel_generation,
            state="disabled"
        )

        self.cancel_btn.grid(row=0, column=1, padx=10)

        # ===========================
        # Audio Player
        # ===========================

        player = ttk.LabelFrame(
            main_frame,
            text=" Player "
        )

        player.pack(fill="x", pady=10)

        controls = ttk.Frame(player)

        controls.pack(
            side="left",
            padx=15,
            pady=15
        )

        self.play_btn = ttk.Button(
            controls,
            text="▶ Play",
            bootstyle="secondary",
            width=10,
            state="disabled",
            command=self.toggle_play
        )

        self.play_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(
            controls,
            text="⏹ Stop",
            bootstyle="secondary",
            width=10,
            state="disabled",
            command=self.stop_playback
        )

        self.stop_btn.grid(row=0, column=1, padx=5)

        ttk.Label(
            controls,
            text="🔊"
        ).grid(row=0, column=2, padx=(15, 5))

        self.volume = ttk.Scale(
            controls,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            length=120,
            command=self.on_volume_change
        )

        self.volume.set(self.player.get_volume())

        self.volume.grid(row=0, column=3, padx=5)

        self.position_label = ttk.Label(
            player,
            text="0:00 / 0:00",
            font=("Segoe UI", 10),
            anchor="e"
        )

        self.position_label.pack(
            side="right",
            padx=20
        )

        # ===========================
        # Status Bar
        # ===========================

        self.status = ttk.Label(
            self.root,
            text="Ready",
            anchor="w",
            bootstyle="inverse-dark"
        )

        self.status.pack(
            fill="x",
            side="bottom"
        )

    # ====================================
    # Settings <-> widgets
    # ====================================

    def apply_settings_to_widgets(self):

        voice = self.settings.get("voice")

        if voice in VOICES:
            self.voice.set(voice)

        self.speed.set(self.settings.get("speed", 1.0))
        self.on_speed_change()

        self.volume.set(self.settings.get("volume", 0.8))
        self.on_volume_change()

        last_folder = self.settings.get("last_pdf_folder")
        if last_folder and os.path.isdir(last_folder):
            os.chdir(last_folder)

    def persist_settings(self):

        self.settings.update(
            voice=self.voice.get(),
            speed=float(self.speed.get()),
            volume=float(self.volume.get()),
            last_output_folder=self.output_folder,
        )

        self.settings.save()

    # ====================================
    # File pickers
    # ====================================

    def select_pdf(self):

        initial = self.settings.get("last_pdf_folder") or os.getcwd()

        file = filedialog.askopenfilename(
            initialdir=initial,
            filetypes=[("PDF Files", "*.pdf")]
        )

        if file:

            self.pdf_path = file

            self.file_label.config(
                text=os.path.basename(file)
            )

            self.settings.set("last_pdf_folder", os.path.dirname(file))

            self.set_status(f"PDF selected: {os.path.basename(file)}")

            log.info("PDF selected: %s", file)

    def select_output_folder(self):

        folder = filedialog.askdirectory(
            initialdir=self.output_folder or os.getcwd()
        )

        if folder:

            self.output_folder = folder

            self.output_label.config(
                text=folder
            )

            self.set_status("Output folder updated.")

    # ====================================
    # Generation lifecycle
    # ====================================

    def start_generation(self):

        if self.worker and self.worker.is_running():
            return

        if not self.pdf_path:

            messagebox.showwarning(
                "No PDF",
                "Please choose a PDF first."
            )

            return

        self.generate_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress.configure(value=0)

        self.worker = GenerationWorker(
            pdf_path=self.pdf_path,
            output_folder=self.output_folder,
            voice=self.voice.get(),
            speed=float(self.speed.get()),
            chunk_size=self.settings.get("chunk_size", 3500),
            cleanup_parts=self.settings.get("cleanup_parts", True),
        )

        # All callbacks fire on the worker thread — marshal to UI thread.
        self.worker.on_progress = lambda p, m="": self.root.after(
            0, lambda: self.update_progress(p, m)
        )
        self.worker.on_status = lambda msg: self.root.after(
            0, lambda: self.set_status(msg)
        )
        self.worker.on_finished = lambda path: self.root.after(
            0, lambda: self.on_generation_finished(path)
        )
        self.worker.on_cancelled = lambda: self.root.after(
            0, self.on_generation_cancelled
        )
        self.worker.on_error = lambda err: self.root.after(
            0, lambda: self.on_generation_error(err)
        )

        self.set_status("Starting generation...")
        self.worker.start()

    def cancel_generation(self):

        if self.worker and self.worker.is_running():
            self.set_status("Cancelling...")
            self.worker.cancel()

    def on_generation_finished(self, output_path):

        self.last_audio_path = output_path
        self.update_progress(100, "Done")
        self.set_status("Completed")
        self.reset_buttons_after_run()

        self.play_btn.config(state="normal")
        self.stop_btn.config(state="normal")

        self.persist_settings()

        messagebox.showinfo(
            "Success",
            f"Audiobook saved at\n\n{output_path}"
        )

        log.info("Generation finished: %s", output_path)

    def on_generation_cancelled(self):

        self.update_progress(0, "")
        self.set_status("Cancelled")
        self.reset_buttons_after_run()

        log.info("Generation was cancelled")

    def on_generation_error(self, error):

        self.set_status("Error")
        self.reset_buttons_after_run()

        if isinstance(error, GenerationCancelled):
            return

        log.exception("Generation error", exc_info=error)

        messagebox.showerror(
            "Error",
            str(error)
        )

    def reset_buttons_after_run(self):

        self.generate_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    # ====================================
    # UI helpers (run on main thread)
    # ====================================

    def set_status(self, message):

        self.status.config(text=message)

    def update_progress(self, value, message=""):

        self.progress.configure(value=value)

        if message:
            self.set_status(message)

    def on_speed_change(self, *_args):

        # The Scale fires this callback during construction, before the
        # companion label exists — bail out until the widget tree is ready.
        if not hasattr(self, "speed_value"):
            return

        value = float(self.speed.get())
        self.speed_value.config(text=f"{value:.1f}x")

    def on_volume_change(self, *_args):

        if not hasattr(self, "volume"):
            return

        self.player.set_volume(float(self.volume.get()))

    # ====================================
    # Player controls
    # ====================================

    def toggle_play(self):

        if not self.last_audio_path:
            return

        if self.player.is_paused:
            self.player.resume()
            self.play_btn.config(text="⏸ Pause")
            return

        if self.player.is_playing:
            self.player.pause()
            self.play_btn.config(text="▶ Play")
            return

        # Fresh start
        try:
            self.player.play(self.last_audio_path)
            self.play_btn.config(text="⏸ Pause")
            self.stop_btn.config(state="normal")
            self.set_status("Playing audiobook...")
        except FileNotFoundError as error:
            messagebox.showerror("Playback Error", str(error))
            log.error(error)

    def stop_playback(self):

        self.player.stop()
        self.play_btn.config(text="▶ Play")
        self.set_status("Stopped")
        self.position_label.config(text="0:00 / 0:00")

    def poll_player(self):
        """Refresh the position label and detect natural track end."""

        if self.player.current_file and self.player.is_playing:

            position = self.player.get_position() or 0.0
            duration = self._get_audio_duration()

            self.position_label.config(
                text=f"{format_duration(position)} / {format_duration(duration)}"
            )

            # When the track finishes on its own, reset the play button.
            if self.player.is_finished():
                self.player.is_playing = False
                self.play_btn.config(text="▶ Play")
                self.position_label.config(text=f"0:00 / {format_duration(duration)}")
                self.set_status("Finished playback")

        self.root.after(_POSITION_POLL_MS, self.poll_player)

    def _get_audio_duration(self):
        """Cached duration lookup for the current file (seconds)."""

        if not self.player.current_file:
            return 0.0

        cache = getattr(self, "_duration_cache", None)
        if cache and cache[0] == self.player.current_file:
            return cache[1]

        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(self.player.current_file)
            duration = len(audio) / 1000.0
        except Exception as error:
            log.warning("Could not read audio duration: %s", error)
            duration = 0.0

        self._duration_cache = (self.player.current_file, duration)
        return duration

    # ====================================
    # Shutdown
    # ====================================

    def on_close(self):

        if self.worker and self.worker.is_running():
            if not messagebox.askyesno(
                "Quit",
                "Generation is still running. Quit and discard progress?"
            ):
                return

            self.worker.cancel()

        try:
            self.player.stop()
        except Exception:
            pass

        try:
            import pygame
            pygame.mixer.quit()
        except Exception:
            pass

        self.persist_settings()
        self.root.destroy()
