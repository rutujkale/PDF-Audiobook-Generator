class PDFAudioBookApp:

    def __init__(self, root):

        self.root = root
        self.root.title("PDF Audiobook Generator")
        self.root.geometry("900x600")
        self.root.minsize(850, 550)

        self.pdf_path = ""

        self.player = AudioPlayer()

        self.create_widgets()