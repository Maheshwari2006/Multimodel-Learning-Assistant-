import pdfplumber
import os

pdf_file = "sample.pdf"

if os.path.exists(pdf_file):
    print("✅ PDF Found")

    with pdfplumber.open(pdf_file) as pdf:
        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        print(text[:5000])

else:
    print("❌ PDF Not Found")