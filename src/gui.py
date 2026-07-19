import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from src.pdf_reader import PDFReader

class PDFAudioBookGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("PDF Audiobook Generator")

        self.root.geometry("1000x700")
        self.root.minsize(900, 650)

        self.pdf_path = ""
        self.output_folder = "output"

        self.create_widgets()

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
            values=[
                "en-US-GuyNeural",
                "en-US-JennyNeural",
                "en-GB-RyanNeural",
                "en-GB-SoniaNeural"
            ],
            width=35
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
            length=220
        )

        self.speed.set(1.0)

        self.speed.grid(
            row=0,
            column=3,
            padx=10
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
        # Generate Button
        # ===========================

        self.generate_btn = ttk.Button(
            main_frame,
            text="Generate Audiobook",
            bootstyle="success",
            width=30,
            command=self.generate_audio
        )

        self.generate_btn.pack(pady=20)

        # ===========================
        # Audio Controls
        # ===========================

        player = ttk.Frame(main_frame)

        player.pack()

        ttk.Button(
            player,
            text="▶ Play",
            bootstyle="secondary",
            state="disabled"
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            player,
            text="⏸ Pause",
            bootstyle="secondary",
            state="disabled"
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            player,
            text="⏹ Stop",
            bootstyle="secondary",
            state="disabled"
        ).grid(row=0, column=2, padx=10)

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

    def select_pdf(self):

        file = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")]
        )

        if file:

            self.pdf_path = file

            self.file_label.config(
                text=os.path.basename(file)
            )

            self.status.config(
                text="PDF Selected"
            )

    # ====================================

    def select_output_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.output_folder = folder

            self.output_label.config(
                text=folder
            )

    # ====================================

    def generate_audio(self):

        if self.pdf_path == "":

            messagebox.showwarning(
                "No PDF",
                "Please choose a PDF first."
            )

            return

        try:

            reader = PDFReader(self.pdf_path)

            reader.open()

            info = reader.extract_info()

            text = reader.extract_text()

            reader.close()

            self.progress["value"] = 100

            self.status.config(
                text="PDF Loaded Successfully"
            )

            messagebox.showinfo(

                "PDF Information",

                f"Title : {info['title']}\n\n"

                f"Author : {info['author']}\n\n"

                f"Pages : {info['pages']}\n\n"

                f"Characters : {len(text)}"

            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )