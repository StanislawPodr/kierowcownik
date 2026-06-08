import shutil
from pathlib import Path

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


def print_missing_files():
    questions = Question.objects.all()

    for question in questions:
        if question.media_url !="" and not Path(question.media_url).is_file():
            print(f"Missing file: ${question.media_url}")
