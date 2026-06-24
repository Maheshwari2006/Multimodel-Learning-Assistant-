import ollama


class FlashcardGenerator:

    def __init__(self, model_name="llama3"):

        self.model_name = model_name

    def generate_flashcards(
        self,
        text,
        num_flashcards=10
    ):

        prompt = f"""
You are an expert educational assistant.

Based on the study material below, create {num_flashcards}
high-quality flashcards for revision.

Requirements:
- Cover the most important concepts.
- Keep questions concise.
- Answers should be short and easy to remember.
- Suitable for exam preparation.

Format:

📌 Flashcard 1

Question:
...

Answer:
...

📌 Flashcard 2

Question:
...

Answer:
...

Study Material:
{text}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]