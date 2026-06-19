import os
import whisper
from moviepy import VideoFileClip

# FFmpeg Path
os.environ["PATH"] += os.pathsep + r"C:\Users\ADMIN\Downloads\ffmpeg-8.1.1-essentials_build\ffmpeg-8.1.1-essentials_build\bin"


class VideoProcessor:

    # Load Whisper model once
    model = whisper.load_model("base")

    @staticmethod
    def extract_text(video_path):
        """
        Extract speech text from video file
        """

        try:
            print("🎬 Loading Video...")

            video = VideoFileClip(video_path)

            audio_path = "temp_audio.wav"

            print("🎵 Extracting Audio From Video...")

            video.audio.write_audiofile(
                audio_path,
                logger=None
            )

            print("🤖 Running Whisper Transcription...")

            result = VideoProcessor.model.transcribe(audio_path)

            text = result["text"]

            # Cleanup temp file
            if os.path.exists(audio_path):
                os.remove(audio_path)

            return text

        except Exception as e:
            print("❌ Error:", e)
            return ""