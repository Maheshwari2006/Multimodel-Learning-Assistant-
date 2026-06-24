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

from study_tools.flashcard_generator import (
    FlashcardGenerator
)

print("=" * 70)
print("🧠 AI FLASHCARD GENERATOR")
print("=" * 70)

with open(
    "sample.txt",
    "r",
    encoding="utf-8"
) as file:

    text = file.read()

print("📄 Study Material Loaded")
print(f"📊 Characters: {len(text)}")

print("\n🤖 Generating Flashcards...\n")

generator = FlashcardGenerator()

flashcards = generator.generate_flashcards(
    text,
    num_flashcards=10
)

print("=" * 70)
print("📚 GENERATED FLASHCARDS")
print("=" * 70)

print(flashcards)

print("\n" + "=" * 70)
print("✅ Flashcard Generation Successful 🚀")
print("=" * 70)