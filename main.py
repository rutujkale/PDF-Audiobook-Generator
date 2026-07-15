import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from src.pdf_reader import PDFReader

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

        generate_btn = tk.Button(
            self.root,
            text="Generate Audiobook",
            width=25,
            height=2,
            command=self.generate_audio
        )

        generate_btn.pack(pady=15)

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

    def generate_audio(self):

        if self.pdf_path == "":

            messagebox.showwarning(
                "Warning",
                "Please select a PDF first."
            )

            return

        try:

            self.status.config(text="Reading PDF...")

            self.root.update()

            text = PDFReader.extract_text(self.pdf_path)

            self.progress["value"] = 40

            self.status.config(
                text=f"Successfully extracted {len(text)} characters."
            )

            messagebox.showinfo(
                "Success",
                f"PDF Loaded Successfully!\n\nCharacters extracted:\n{len(text)}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )


def main():

    root = tk.Tk()

    app = PDFAudioBookApp(root)

    root.mainloop()


if __name__ == "__main__":

    main()