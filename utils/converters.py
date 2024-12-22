import os
import subprocess


def convert_to_mp3(input_file: str, output_file: str):
    # Delete the output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Convert the OGG file to MP3 using FFmpeg
    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-acodec",
        "libmp3lame",
        output_file,
    ]
    subprocess.run(command, check=True)
    return output_file
