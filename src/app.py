import ttkbootstrap as ttk
from src.gui import MainWindow


class App:
    def __init__(self):
        self.root = ttk.Window(themename="darkly")
        self.root.title("PDF Audiobook Generator")
        self.root.geometry("900x600")

        MainWindow(self.root)

    def run(self):
        self.root.mainloop()