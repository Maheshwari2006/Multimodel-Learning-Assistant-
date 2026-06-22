import os
import sys

# Enable UTF-8 for emoji support
sys.stdout.reconfigure(encoding="utf-8")

from text_processing.cleaner import TextCleaner
from text_processing.chunker import TextChunker

file_path = "sample.txt"

print("📄 Checking Text File...")

if not os.path.exists(file_path):
    print("❌ File Not Found:", file_path)
    exit()

print("✅ File Exists")
print("📏 File Size:", os.path.getsize(file_path), "bytes")

try:
    print("\n📖 Reading File...\n")

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    print("🧹 Cleaning Text...")
    clean_text = TextCleaner.clean_text(text)

    print("✂️ Creating Chunks...")
    chunks = TextChunker.chunk_text(clean_text)

    print(f"\n📦 Total Chunks Created: {len(chunks)}")

    print("\n🔍 ===== SAMPLE CHUNKS =====")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n📌 Chunk {i+1}:\n")
        print(chunk)
        print("-" * 50)

    print("\n✅ Text Chunking Successful 🚀")

except Exception as e:
    print("❌ Error:", e)