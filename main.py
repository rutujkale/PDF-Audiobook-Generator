from tkinter import Tk

from src.gui import PDFAudioBookGUI


def main():

    root = Tk()

    app = PDFAudioBookGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()