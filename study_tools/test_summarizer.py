import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from study_tools.summarizer import Summarizer

print("=" * 70)
print("📚 MULTIMODAL LEARNING ASSISTANT - AI SUMMARIZER")
print("=" * 70)

file_path = "sample.txt"

with open(
    file_path,
    "r",
    encoding="utf-8"
) as file:

    text = file.read()

print(f"\n📄 Loaded File: {file_path}")
print(f"📊 Total Characters: {len(text)}")

print("\n🤖 Generating Summary...\n")

summarizer = Summarizer()

summary = summarizer.summarize(text)

print("=" * 70)
print("📝 GENERATED SUMMARY")
print("=" * 70)

print(summary)

print("\n" + "=" * 70)
print("✅ Summarization Completed Successfully 🚀")
print("=" * 70)