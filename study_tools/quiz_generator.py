import ollama


class QuizGenerator:

    def __init__(self, model_name="llama3"):

        self.model_name = model_name

    def generate_quiz(
        self,
        text,
        num_questions=5
    ):

        prompt = f"""
You are an expert quiz generator.

Based on the content below, generate {num_questions}
multiple-choice questions.

Format:

Q1. Question

A) Option
B) Option
C) Option
D) Option

Answer: Correct Option

Content:
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