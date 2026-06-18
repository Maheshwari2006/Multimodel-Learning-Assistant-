import os
import sys
import pytesseract

# Enable UTF-8 for emojis
sys.stdout.reconfigure(encoding="utf-8")

# Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from file_processing.image_processor import ImageProcessor

image_file = "sample.jpeg"

print("🖼️ Checking Image File...")

if not os.path.exists(image_file):
    print("❌ Image File Not Found:", image_file)
    print("\n📂 Files in Folder:")
    print(os.listdir())
    exit()

print("✅ File Exists:", os.path.exists(image_file))
print("📄 File Size:", os.path.getsize(image_file), "bytes")

print("\n🔍 Extracting Text From Image...\n")

text = ImageProcessor.extract_text(image_file)

print("🔤 Extracted Characters:", len(text))

print("\n📖 ===== IMAGE TEXT PREVIEW =====\n")
print(text[:500])

print("\n✅ OCR Processing Successful 🚀")