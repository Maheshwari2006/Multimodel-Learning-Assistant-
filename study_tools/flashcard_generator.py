
import json
import re
import ollama


class FlashcardGenerator:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate_flashcards(self, text, num_flashcards=10):
        prompt = f"""
You are an expert educational assistant.

Create exactly {num_flashcards} flashcards from the study material.

Return ONLY a valid JSON array, without Markdown code fences.
Each item must have:
- "question": a concise question
- "answer": a short, accurate answer

Example:
[
  {{"question": "What is Python?", "answer": "A high-level programming language."}},
  {{"question": "What is a variable?", "answer": "A named location used to store data."}}
]

Use only information supported by the study material.
If the material is short, create fewer meaningful cards rather than inventing facts.

Study material:
{text}
"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )

        content = response["message"]["content"].strip()

        # Remove Markdown fences if the model includes them.
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content).strip()

        data = json.loads(content)

        # Support either a JSON array or an object containing flashcards.
        if isinstance(data, dict):
            data = data.get("flashcards", data.get("cards", []))

        if not isinstance(data, list):
            raise ValueError("Ollama did not return a flashcard list.")

        flashcards = []

        for card in data:
            if not isinstance(card, dict):
                continue

            question = card.get("question") or card.get("front") or card.get("term")
            answer = card.get("answer") or card.get("back") or card.get("definition")

            if question and answer:
                flashcards.append({
                    "question": str(question).strip(),
                    "answer": str(answer).strip()
                })

        return flashcards
