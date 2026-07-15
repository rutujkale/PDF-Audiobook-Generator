import fitz


class PDFReader:

    @staticmethod
    def extract_text(pdf_path):

        try:

            document = fitz.open(pdf_path)

            text = ""

            for page in document:

                text += page.get_text()

            document.close()

            if text.strip() == "":

                raise Exception(
                    "No readable text found inside this PDF."
                )

            return text

        except Exception as e:

            raise Exception(
                f"Unable to read PDF.\n{e}"
            )