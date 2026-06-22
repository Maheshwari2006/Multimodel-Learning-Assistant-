import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

# Add project root path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from rag.qa_system import (
    RAGQuestionAnswering
)

print("🤖 Initializing RAG System...")

context = """
Machine Learning is a branch of Artificial Intelligence.

Deep Learning uses Neural Networks.

Neural Networks learn patterns from data.

Python is widely used in Data Science.
"""

question = (
    "What is Deep Learning?"
)

print("✅ Context Loaded")
print("❓ Question:", question)

print("\n🔍 Generating Answer...\n")

qa = RAGQuestionAnswering(
    model_name="llama3"
)

answer = qa.answer_question(
    context,
    question
)

print("📝 ===== ANSWER =====\n")

print(answer)

print("\n✅ RAG Question Answering Successful 🚀")



