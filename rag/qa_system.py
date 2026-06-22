import ollama


class RAGQuestionAnswering:

    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def answer_question(self, context, question):

        prompt = f"""
You are a helpful AI assistant.

Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{question}

Answer:
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