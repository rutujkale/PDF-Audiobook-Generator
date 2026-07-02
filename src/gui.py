import os

import ttkbootstrap as ttk
from tkinter import filedialog


class MainWindow:

    def __init__(self, root):
        self.root = root
        self.root.configure(padx=30, pady=20)

        self.selected_pdf = None
        self.filename = ttk.StringVar(value="📄 No PDF Selected")

        self.create_header()
        self.create_file_section()
        self.create_settings_section()
        self.create_action_section()

    def create_header(self):
        """Application Title"""

        title = ttk.Label(
            self.root,
            text="📚 PDF Audiobook Generator",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(10, 5))

        subtitle = ttk.Label(
            self.root,
            text="Convert any PDF into a natural sounding audiobook",
            font=("Segoe UI", 11)
        )
        subtitle.pack(pady=(0, 25))

    def create_file_section(self):
        """PDF Selection Section"""

        select_button = ttk.Button(
            self.root,
            text="📂 Select PDF",
            bootstyle="primary",
            command=self.select_pdf
        )
        select_button.pack(pady=10)

        file_label = ttk.Label(
            self.root,
            textvariable=self.filename,
            font=("Segoe UI", 10)
        )
        file_label.pack(pady=(5, 20))

    def create_settings_section(self):
        """Settings Section"""

        # Voice Label
        voice_label = ttk.Label(
            self.root,
            text="Voice",
            font=("Segoe UI", 11, "bold")
        )
        voice_label.pack(anchor="w")

        # Voice Dropdown
        self.voice_box = ttk.Combobox(
            self.root,
            values=[
                "en-US-AriaNeural",
                "en-US-GuyNeural",
                "en-IN-NeerjaNeural",
                "en-IN-PrabhatNeural"
            ],
            state="readonly"
        )

        self.voice_box.current(0)
        self.voice_box.pack(fill="x", pady=(5, 15))

        # Speed Label
        speed_label = ttk.Label(
            self.root,
            text="Speech Speed",
            font=("Segoe UI", 11, "bold")
        )
        speed_label.pack(anchor="w")

        # Speed Slider
        self.speed_slider = ttk.Scale(
            self.root,
            from_=-50,
            to=50
        )
        self.speed_slider.set(0)
        self.speed_slider.pack(fill="x", pady=(5, 25))

    def create_action_section(self):
        """Bottom Buttons"""

        self.generate_button = ttk.Button(
            self.root,
            text="🎙 Generate Audiobook",
            bootstyle="success",
            state="disabled"
        )

        self.generate_button.pack(fill="x", ipady=8)

        self.progress = ttk.Progressbar(
            self.root,
            mode="determinate",
            maximum=100
        )

        self.progress.pack(fill="x", pady=20)

    def select_pdf(self):
        """Open File Dialog"""

        file_path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if file_path:
            self.selected_pdf = file_path

            filename = os.path.basename(file_path)

            self.filename.set(f"📄 {filename}")

            self.generate_button.config(state="normal")