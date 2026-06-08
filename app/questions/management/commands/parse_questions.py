import pandas as pd
from django.core.management import BaseCommand

from questions.models import Categories, Question


class Command(BaseCommand):
    description = 'Question Parser'
    help = 'Takes data from xlsx file from https://www.gov.pl/web/infrastruktura/prawo-jazdy and saves it to database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', help='path to file with questions')
        parser.add_argument('--reset', action='store_true', help='reset database')

    def handle(self, *args, **kwargs):
        if kwargs['reset']:
            Question.objects.all().delete()
            Categories.objects.all().delete()
        file_path = kwargs['file_path']
        questions = pd.read_excel(file_path)
        questions = questions.dropna(subset=['Pytanie'])

        def save_question(question):
            if question._2 is None or str(question._2).strip() == "":
                return
            categories = str(question.Kategorie).split(',')
            returned_categories = []
            for category in categories:
                cat_obj, created = Categories.objects.get_or_create(symbol=category)
                returned_categories.append(cat_obj)

            new_question, created = Question.objects.get_or_create(
                question_number=question._2,
                question_text=question.Pytanie,
                is_basic=pd.isna(question._4) or str(question._4).strip() == "",
                answer_A=question._4,
                answer_B=question._5,
                answer_C=question._6,
                correct_answer=question._7,
                media_url=question.Media,
                url_type=Question.UrlType.video if str(question.Media).endswith(".wmv") else Question.UrlType.photo,
                number_of_points=question._10,
            )
            if created:
                new_question.category.add(*returned_categories)

        for i in questions.itertuples():
            save_question(i)
