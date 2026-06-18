from docx import Document
import os

doc_file = "sample.docx"   # Change if your filename is different

print("Current Folder:", os.getcwd())
print("\nFiles in Folder:")
print(os.listdir())

print("\nChecking File...")

if os.path.exists(doc_file):
    print("✅ File Exists")
    print("📄 File Size:", os.path.getsize(doc_file), "bytes")

    try:
        doc = Document(doc_file)

        print("\n===== DOCUMENT CONTENT =====\n")

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                print(text)

        print("\n✅ DOCX Reading Successful")

    except Exception as e:
        print("❌ Error Reading DOCX:", e)

else:
    print("❌ File Not Found:", doc_file)