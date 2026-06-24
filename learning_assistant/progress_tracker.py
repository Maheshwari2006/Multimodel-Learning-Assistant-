class ProgressTracker:
    def __init__(self):

        self.completed_topics = []

    def mark_completed(
    self,
    topic
):

        if topic not in self.completed_topics:

            self.completed_topics.append(
                topic
            )

            return f"✅ {topic} completed"

        return f"⚠️ {topic} already completed"

    def get_progress(
        self,
        total_topics
    ):

        if total_topics == 0:
            return 0

        completed = len(
            self.completed_topics
        )

        progress = (
            completed / total_topics
        ) * 100

        return round(
            progress,
            2
        )

    def show_dashboard(
        self,
        total_topics
    ):

        progress = self.get_progress(
            total_topics
        )

        print("\n" + "=" * 60)
        print("📊 STUDY PROGRESS DASHBOARD")
        print("=" * 60)

        print(
            f"📚 Completed Topics : {len(self.completed_topics)}"
        )

        print(
            f"🎯 Total Topics     : {total_topics}"
        )

        print(
            f"📈 Progress         : {progress}%"
        )

        print("\n✅ Completed Topics:")

        for topic in self.completed_topics:

            print(
                f"   • {topic}"
            )

        print("=" * 60)

