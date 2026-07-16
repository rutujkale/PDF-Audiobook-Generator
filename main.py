import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from src.pdf_reader import PDFReader
from src.tts import TextToSpeech
import threading

class PDFAudioBookApp:

    def __init__(self, root):

        self.root = root
        self.root.title("PDF Audiobook Generator")
        self.root.geometry("900x600")
        self.root.minsize(850,550)

        self.pdf_path = ""

        self.create_widgets()

    def create_widgets(self):

        title = tk.Label(
            self.root,
            text="PDF Audiobook Generator",
            font=("Segoe UI",22,"bold")
        )

        title.pack(pady=20)

        subtitle = tk.Label(
            self.root,
            text="Convert any PDF into a natural sounding audiobook.",
            font=("Segoe UI",11)
        )

        subtitle.pack()

        ttk.Separator(self.root).pack(fill="x", pady=20)

        self.file_label = tk.Label(
            self.root,
            text="No PDF Selected",
            fg="gray",
            font=("Segoe UI",11)
        )

        self.file_label.pack(pady=10)

        browse_btn = tk.Button(
            self.root,
            text="Browse PDF",
            width=20,
            command=self.select_pdf
        )

        browse_btn.pack(pady=5)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=500,
            mode="determinate"
        )

        self.progress.pack(pady=25)

        self.generate_btn = tk.Button(
            self.root,
            text="Generate Audiobook",
            width=25,
            height=2,
            command=self.generate_audio
        )

        self.generate_btn.pack(pady=15)

        player_frame = tk.Frame(self.root)

        player_frame.pack(pady=30)

        tk.Button(
            player_frame,
            text="Play",
            width=12
        ).grid(row=0,column=0,padx=10)

        tk.Button(
            player_frame,
            text="Pause",
            width=12
        ).grid(row=0,column=1,padx=10)

        tk.Button(
            player_frame,
            text="Stop",
            width=12
        ).grid(row=0,column=2,padx=10)

        status = tk.Label(
            self.root,
            text="Status : Waiting...",
            fg="blue"
        )

        status.pack(side="bottom", pady=15)

        self.status = status

    def select_pdf(self):

        file = filedialog.askopenfilename(

            title="Select PDF",

            filetypes=[
                ("PDF Files","*.pdf")
            ]
        )

        if file:

            self.pdf_path = file

            filename = os.path.basename(file)

            self.file_label.config(text=filename)

            self.status.config(text="PDF Selected")

    def update_status(self, text=None, progress=None):
        """
        Safely update Tkinter widgets from a background thread.
        """

        def update():

            if text is not None:
                self.status.config(text=text)

            if progress is not None:
                self.progress["value"] = progress

        self.root.after(0, update)


    def generate_audio(self):

        if self.pdf_path == "":

            messagebox.showwarning(
                "Warning",
                "Please select a PDF first."
            )

            return

        self.generate_btn.config(state="disabled")

        thread = threading.Thread(
            target=self.generate_audio_thread,
            daemon=True
        )

        thread.start()


    def generate_audio_thread(self):

        try:

            # Reading PDF
            self.update_status(
                text="Reading PDF...",
                progress=10
            )

            text = PDFReader.extract_text(
                self.pdf_path
            )

            # Generating Audio
            self.update_status(
                text="Generating Audiobook...",
                progress=40
            )

            tts = TextToSpeech()

            output = tts.create_audio(text)

            # Finished
            self.update_status(
                text="Completed!",
                progress=100
            )

            self.root.after(
                0,
                lambda: self.generate_btn.config(
                    state="normal"
                )
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    f"Audiobook saved successfully!\n\n{output}"
                )
            )

        except Exception as e:

            self.update_status(
                text="Failed!",
                progress=0
            )

            self.root.after(
                0,
                lambda: self.generate_btn.config(
                    state="normal"
                )
            )

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error",
                    str(e)
                )
            )


def main():

    root = tk.Tk()

    app = PDFAudioBookApp(root)

    root.mainloop()


if __name__ == "__main__":

    main()