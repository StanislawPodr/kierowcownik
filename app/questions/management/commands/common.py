import os
import shutil
from pathlib import Path

from moviepy import VideoFileClip

from questions.models import Question


def flatten_file_structure(directory):
    path = Path(directory)
    for file in path.rglob('*'):
        if file.is_file():
            if file.parent == path:
                continue
            shutil.move(str(file), str(path / file.name))
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(str(item))

def convert_wmv_to_mp4(file_path):
    full_path = str(Path(file_path).resolve())
    output_path = full_path.replace('.wmv', '.mp4')
    clip = VideoFileClip(str(file_path))
    clip.write_videofile(str(output_path), codec="libx264")
    clip.close()
    os.remove(full_path)


def directory_convert_wmv_to_mp4(directory):
    path = Path(directory)
    for file in path.rglob('*.wmv'):
        if file.is_file():
            convert_wmv_to_mp4(file)

def print_missing_files():
    questions = Question.objects.all()

    for question in questions:
        if question.media_url !="" and not Path(question.media_url).is_file():
            print(f"Missing file: ${question.media_url}")
