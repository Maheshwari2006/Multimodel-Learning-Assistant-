import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from file_processing.video_processor import VideoProcessor

video_file = "sample.mp4"

print("🎥 Checking Video File...")

if os.path.exists(video_file):

    print("✅ File Exists")
    print("📄 File Size:", os.path.getsize(video_file), "bytes")

    print("\n🎬 Processing Video...\n")

    text = VideoProcessor.extract_text(video_file)

    print("\n📝 ===== VIDEO TRANSCRIPT =====\n")

    print(text)

    print("\n🔤 Extracted Characters:", len(text))

    print("\n✅ Video Processing Successful 🚀")

else:
    print("❌ Video File Not Found!")