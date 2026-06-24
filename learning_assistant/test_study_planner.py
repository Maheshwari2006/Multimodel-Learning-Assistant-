import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

# Add project root to Python path

sys.path.append(
os.path.dirname(
os.path.dirname(
os.path.abspath(__file__)
)
)
)

from learning_assistant.study_planner import StudyPlanner
from learning_assistant.progress_tracker import ProgressTracker

print("=" * 70)
print("🎓 AI STUDY ASSISTANT")
print("=" * 70)

# Generate Study Plan

topic = """
Machine Learning, Deep Learning, Neural Networks,
Natural Language Processing, Computer Vision,
Reinforcement Learning, Generative AI,
Transformers, LLMs, AI Ethics and Bias,
AI in Healthcare, AI in Finance,
AI in Robotics, AI in Education,
AI in Cybersecurity, AI in Gaming,
AI in Agriculture, AI in Climate Change
"""

days = 30

print(f"\n📚 Topic      : {topic}")
print(f"📅 Duration   : {days} Days")

print("\n🤖 Generating Personalized Study Plan...\n")

planner = StudyPlanner()

plan = planner.generate_plan(
topic,
days
)

print("=" * 70)
print("📝 GENERATED STUDY PLAN")
print("=" * 70)

print(plan)

# Track Progress

tracker = ProgressTracker()

print("\n📈 Updating Learning Progress...\n")

print(
tracker.mark_completed(
"Introduction to AI"
)
)

print(
tracker.mark_completed(
"Machine Learning Basics"
)
)

print(
tracker.mark_completed(
"Supervised Learning"
)
)

print(
tracker.mark_completed(
"Unsupervised Learning"
)
)

print(
tracker.mark_completed(
"Model Evaluation"
)
)

# Duplicate test

print(
tracker.mark_completed(
"Machine Learning Basics"
)
)

tracker.show_dashboard(
total_topics=10
)

print("\n🏆 Keep Learning & Stay Consistent!")
print("🚀 AI Study Assistant Completed Successfully")
print("=" * 70)

