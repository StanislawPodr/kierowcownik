from zipfile import ZipFile
from pathlib import Path
from django.core.management import BaseCommand
import os.path
from questions.management.commands.common import flatten_file_structure, print_missing_files, \
    directory_convert_wmv_to_mp4

from kierowcownik.settings import MEDIA_FOLDER


class Command(BaseCommand):
    help = 'Add resources for questions'

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', help='zip file with resources for questions')
        parser.add_argument('--reset',action='store_true', help='deletes old files')

    def handle(self, *args, **kwargs):
        end_url = str(MEDIA_FOLDER)

        if not os.path.exists(end_url):
            os.makedirs(end_url)
        if kwargs['reset']:
            for item in Path(end_url).iterdir():
                item.unlink()

        for file in kwargs['files']:
            with ZipFile(file, 'r') as zObject:
                zObject.extractall(path=end_url)

        flatten_file_structure(end_url)
        directory_convert_wmv_to_mp4(end_url)
