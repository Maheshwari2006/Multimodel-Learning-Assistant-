import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

print("🚀 Script Started")

from file_processing.audio_processor import AudioProcessor

audio_file = "sample.mp3"

print("🎵 Checking Audio File...")

if os.path.exists(audio_file):

    print("✅ File Exists")
    print("📄 File Size:", os.path.getsize(audio_file))

    text = AudioProcessor.extract_text(audio_file)

    print("\n📝 TRANSCRIBED TEXT:\n")
    print(text)

    print("\n🔤 Characters:", len(text))

else:
    print("❌ Audio File Not Found")