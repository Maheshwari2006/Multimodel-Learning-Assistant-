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

from learning_assistant.recommendation_engine import (
    RecommendationEngine
)

from learning_assistant.recommendation_engine import (
RecommendationEngine
)

print("=" * 70)
print("🎯 AI LEARNING RECOMMENDATION SYSTEM")
print("=" * 70)

quiz_scores = {

"Machine Learning": 85,
"Deep Learning": 55,
"Neural Networks": 70,
"Computer Vision": 45,
"Natural Language Processing": 92,
"Generative AI": 60

}

completed_topics = [

"Machine Learning",
"Natural Language Processing"


]

print("\n📊 QUIZ PERFORMANCE")
print("-" * 70)

for topic, score in quiz_scores.items():

    print(
    f"📚 {topic:<30} ➜ {score}%"
)


print("\n✅ COMPLETED TOPICS")
print("-" * 70)

for topic in completed_topics:

    print(
    f"✔️ {topic}"
)

print("\n🤖 Generating Personalized Recommendations...\n")

engine = RecommendationEngine()

recommendations = engine.recommend(
quiz_scores,
completed_topics
)

print("=" * 70)
print("🎯 AI LEARNING RECOMMENDATIONS")
print("=" * 70)

for i, recommendation in enumerate(
recommendations,
start=1
):

    print(
    f"{i}. {recommendation}"
)

print("\n" + "=" * 70)
print("🚀 Recommendation Analysis Completed Successfully")
print("=" * 70)
