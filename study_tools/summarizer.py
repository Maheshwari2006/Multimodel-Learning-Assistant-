import ollama


class StudySummarizer:

    def __init__(
        self,
        model_name="llama3"
    ):
        self.model_name = model_name

    def summarize(
        self,
        text
    ):

        prompt = f"""
Summarize the following study material.

Provide:

1. Short Summary
2. Key Points
3. Important Concepts
4. Easy Explanation

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
    

