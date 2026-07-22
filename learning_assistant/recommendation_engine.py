class RecommendationEngine:

    def recommend(
        self,
        quiz_scores,
        completed_topics
    ):

        recommendations = []

        print("\n🤖 Analyzing Learning Performance...\n")

        for topic, score in quiz_scores.items():

            if score < 40:

                recommendations.append(
                    f"🚨 High Priority Revision: {topic}"
                )

            elif score < 60:

                recommendations.append(
                    f"📚 Revise Concepts: {topic}"
                )

            elif score < 80:

                recommendations.append(
                    f"📝 Practice More Questions: {topic}"
                )

            else:

                recommendations.append(
                    f"✅ Strong Understanding: {topic}"
                )

        remaining_topics = [

            topic

            for topic in quiz_scores.keys()

            if topic not in completed_topics

        ]

        if remaining_topics:

            recommendations.append(
                f"🎯 Recommended Next Topic: {remaining_topics[0]}"
            )

        completed_count = len(
            completed_topics
        )

        total_topics = len(
            quiz_scores
        )

        progress = (
            completed_count / total_topics
        ) * 100

        recommendations.append(
            f"📈 Overall Progress: {round(progress, 2)}%"
        )

        if progress >= 80:

            recommendations.append(
                "🏆 Excellent Progress! Start Advanced Projects."
            )

        elif progress >= 50:

            recommendations.append(
                "🚀 Good Progress! Continue Consistent Learning."
            )

        else:

            recommendations.append(
                "💪 Focus on Completing More Topics."
            )

        return recommendations

