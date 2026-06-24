import ollama


class StudyPlanner:

    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate_plan(self, topic, days):

        prompt = f"""
Create a detailed {days}-day study plan for:

{topic}

Requirements:
- Day-wise schedule
- Beginner friendly
- Include revision days
- Include practice tasks
- Include milestones
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