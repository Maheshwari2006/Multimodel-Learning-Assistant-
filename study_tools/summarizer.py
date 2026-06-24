import ollama

class Summarizer:

    def __init__(self, model_name="llama3"):

        self.model_name = model_name

    def summarize(self, text):

        prompt = f"""
You are an intelligent study assistant.

Analyze the given content and provide:

1. Short Summary
2. Key Points
3. Important Concepts
4. Easy Explanation

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