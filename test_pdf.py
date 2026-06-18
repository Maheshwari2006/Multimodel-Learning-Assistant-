import sys
sys.stdout.reconfigure(encoding="utf-8")

import pdfplumber


class PDFProcessor:

    @staticmethod
    def extract_text(pdf_path):
        """
        📄 Extract text from PDF file
        """

        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:

                print(f"📂 Opening PDF: {pdf_path}")
                print(f"📑 Total Pages: {len(pdf.pages)}")

                for page_num, page in enumerate(pdf.pages, start=1):

                    print(f"📖 Reading Page {page_num}...")

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

                print("✅ PDF Reading Successful")

            return text

        except Exception as e:
            print(f"❌ Error Reading PDF: {e}")
            return ""