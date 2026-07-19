import ttkbootstrap as ttk

from src.gui import PDFAudioBookGUI


def main():

    root = ttk.Window(themename="darkly")

    PDFAudioBookGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()