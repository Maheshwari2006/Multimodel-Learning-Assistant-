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

from study_tools.quiz_generator import (
    QuizGenerator
)

print("=" * 70)
print("🧠 AI QUIZ GENERATOR")
print("=" * 70)

with open(
    "sample.txt",
    "r",
    encoding="utf-8"
) as file:

    text = file.read()

print("📄 Study Material Loaded")
print(f"📊 Characters: {len(text)}")

print("\n🤖 Generating Quiz...\n")

generator = QuizGenerator()

quiz = generator.generate_quiz(
    text,
    num_questions=5
)

print("=" * 70)
print("📝 GENERATED QUIZ")
print("=" * 70)

print(quiz)

print("\n" + "=" * 70)
print("✅ Quiz Generation Successful 🚀")
print("=" * 70)