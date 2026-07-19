import fitz


class PDFReader:

    def __init__(self, pdf_path):

        self.pdf_path = pdf_path

        self.document = None

    def open(self):

        self.document = fitz.open(self.pdf_path)

    def close(self):

        if self.document:

            self.document.close()

    def page_count(self):

        if not self.document:

            self.open()

        return len(self.document)

    def extract_text(self):

        if not self.document:

            self.open()

        text = ""

        for page in self.document:

            text += page.get_text("text")

        return text.strip()

    def extract_info(self):

        if not self.document:

            self.open()

        metadata = self.document.metadata

        return {

            "title": metadata.get("title", "Unknown"),

            "author": metadata.get("author", "Unknown"),

            "pages": len(self.document)
        }