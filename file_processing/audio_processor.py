import whisper
import os

# Add FFmpeg to PATH
os.environ["PATH"] += os.pathsep + r"C:\Users\ADMIN\Downloads\ffmpeg-8.1.1-essentials_build\ffmpeg-8.1.1-essentials_build\bin"

class AudioProcessor:

    model = whisper.load_model("base")

    @staticmethod
    def extract_text(audio_path):

        try:
            result = AudioProcessor.model.transcribe(audio_path)

            return result["text"]

        except Exception as e:
            print("❌ Error:", e)
            return ""