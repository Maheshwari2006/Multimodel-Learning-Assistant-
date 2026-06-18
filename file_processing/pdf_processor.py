import pdfplumber


class PDFProcessor:

    @staticmethod
    def extract_text(pdf_path):
        """
        Extract text from PDF file
        """

        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

            return text

        except Exception as e:
            print(f"Error: {e}")
            return ""