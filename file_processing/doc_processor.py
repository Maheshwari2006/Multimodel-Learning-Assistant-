from docx import Document


class DOCProcessor:

    @staticmethod
    def extract_text(doc_path):
        """
        Extract text from DOCX file
        """

        text = ""

        try:
            doc = Document(doc_path)

            for para in doc.paragraphs:
                text += para.text + "\n"

            return text

        except Exception as e:
            print(f"Error: {e}")
            return ""