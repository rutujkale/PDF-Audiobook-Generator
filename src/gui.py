import ttkbootstrap as ttk
from tkinter import filedialog


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.selected_pdf = None

        # Title
        title = ttk.Label(
            root,
            text="📚 PDF Audiobook Generator",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=30)

        # Select PDF Button
        self.select_button = ttk.Button(
            root,
            text="Select PDF",
            bootstyle="primary",
            command=self.select_pdf
        )
        self.select_button.pack(pady=20)

        # File Name Label
        self.file_label = ttk.Label(
            root,
            text="No PDF Selected",
            font=("Segoe UI", 10)
        )
        self.file_label.pack(pady=10)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select a PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if file_path:
            self.selected_pdf = file_path
            self.file_label.config(text=file_path)