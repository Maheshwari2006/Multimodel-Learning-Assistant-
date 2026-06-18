import os
import sys

# Enable UTF-8 for emojis
sys.stdout.reconfigure(encoding="utf-8")

from file_processing.ppt_processor import PPTProcessor

ppt_file = "sample.pptx"

print("📂 Checking PPT File...")
print("✅ File Exists:", os.path.exists(ppt_file))
print("📄 File Size:", os.path.getsize(ppt_file), "bytes")

print("\n📊 Extracting Text From PPT...\n")

text = PPTProcessor.extract_text(ppt_file)

print("🔤 Extracted Characters:", len(text))

print("\n📖 ===== PPT CONTENT PREVIEW =====\n")

print(text[:50000])

print("\n✅ PPT Reading Successful 🚀")