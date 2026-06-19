import os
import subprocess

os.environ["PATH"] += os.pathsep + r"C:\Users\ADMIN\Downloads\ffmpeg-8.1.1-essentials_build\ffmpeg-8.1.1-essentials_build\bin"

result = subprocess.run(
    ["ffmpeg", "-version"],
    capture_output=True,
    text=True
)

print(result.stdout[:200])
import os
import subprocess

os.environ["PATH"] += os.pathsep + r"C:\Users\ADMIN\Downloads\ffmpeg-8.1.1-essentials_build\ffmpeg-8.1.1-essentials_build\bin"

result = subprocess.run(
    ["ffmpeg", "-version"],
    capture_output=True,
    text=True
)

print(result.stdout[:200])