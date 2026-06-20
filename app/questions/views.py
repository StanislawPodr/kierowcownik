from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Categories, Question
from .serializers import QuestionSerializer

BASIC_COUNT = 20
SPECIALIST_COUNT = 12

def _sample_questions(queryset, count):
    """
    Losuje `count` pytań z podanego querysetu.
    Jeśli pytań jest mniej niż `count`, zwraca wszystkie (w losowej kolejności).
    """
    return queryset.order_by('?')[:count]

class WordExamView(APIView):
    """
    GET /api/questions/exam/word/

    Zwraca test w formacie egzaminu na prawo jazdy kat. B:
    20 losowych pytań podstawowych + 12 losowych specjalistycznych z kategorii B.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            category_b = Categories.objects.get(symbol__iexact='B')
        except Categories.DoesNotExist:
            return Response(
                {'detail': 'Kategoria B nie istnieje w bazie danych.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        base_qs = Question.objects.filter(category=category_b)

        basic_qs = base_qs.filter(is_basic=True)
        specialist_qs = base_qs.filter(is_basic=False)

        basic_questions = list(_sample_questions(basic_qs, BASIC_COUNT))
        specialist_questions = list(_sample_questions(specialist_qs, SPECIALIST_COUNT))

        all_questions = basic_questions + specialist_questions

        return Response({
            'category': 'B',
            'basic_count': len(basic_questions),
            'specialist_count': len(specialist_questions),
            'total': len(all_questions),
            'questions': QuestionSerializer(all_questions, many=True).data,
        })


class CategoryExamView(APIView):
    """
    GET /api/questions/exam/category/<symbol>/

    Zwraca losowy test z podanej kategorii:
    20 pytań podstawowych + 12 specjalistycznych (lub mniej, jeśli baza nie ma tylu).
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, symbol):
        category = get_object_or_404(Categories, symbol__iexact=symbol)

        base_qs = Question.objects.filter(category=category)

        basic_qs = base_qs.filter(is_basic=True)
        specialist_qs = base_qs.filter(is_basic=False)

        basic_questions = list(_sample_questions(basic_qs, BASIC_COUNT))
        specialist_questions = list(_sample_questions(specialist_qs, SPECIALIST_COUNT))

        all_questions = basic_questions + specialist_questions

        return Response({
            'category': category.symbol,
            'basic_count': len(basic_questions),
            'specialist_count': len(specialist_questions),
            'total': len(all_questions),
            'questions': QuestionSerializer(all_questions, many=True).data,
        })


class CategoryListView(APIView):
    """
    GET /api/questions/categories/

    Zwraca listę wszystkich dostępnych kategorii.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        from .serializers import CategorySerializer
        categories = Categories.objects.all().order_by('symbol')
        return Response({'categories': CategorySerializer(categories, many=True).data})
    
class CategoryQuestionsView(APIView):
    """
    GET /api/questions/category/<symbol>/
    Zwraca wszystkie pytania z podanej kategorii.
    """
    permission_classes = (permissions.AllowAny,)
 
    def get(self, request, symbol):
        category = get_object_or_404(Categories, symbol__iexact=symbol)
        questions = Question.objects.filter(category=category).order_by('question_number')
        return Response(QuestionSerializer(questions, many=True).data)
    
class CategoryQuestionsMetaView(APIView):
    """
    GET /api/questions/category/<symbol>/meta/
    Zwraca metadane o pytaniach w kategorii .
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, symbol):
        category = get_object_or_404(Categories, symbol__iexact=symbol)
        qs = Question.objects.filter(category=category)
        points = list(
            qs.order_by('number_of_points')
              .values_list('number_of_points', flat=True)
              .distinct()
        )
        return Response({
            'category': category.symbol,
            'total': qs.count(),
            'basic_count': qs.filter(is_basic=True).count(),
            'specialist_count': qs.filter(is_basic=False).count(),
            'points': points,
        })


class CategoryQuestionSequentialView(APIView):
    """
    GET /api/questions/category/<symbol>/sequential/
    Zwraca pytanie z danej pozycji (offset) w przefiltrowanym zbiorze pytań kategorii (sekwencyjne ładowanie pytań w trybie nauki).
    - offset: pozycja pytania w przefiltrowanej liście (domyślnie 0)
    - type: 'basic' | 'specialist'
    - points: 
    - ids: lista ID pytań oddzielona przecinkami, np. ?ids=12,45,67
    (sortowanie po question number)
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, symbol):
        category = get_object_or_404(Categories, symbol__iexact=symbol)
        qs = Question.objects.filter(category=category)

        q_type = request.query_params.get('type')
        if q_type == 'basic':
            qs = qs.filter(is_basic=True)
        elif q_type == 'specialist':
            qs = qs.filter(is_basic=False)

        points_param = request.query_params.get('points')
        if points_param is not None:
            try:
                qs = qs.filter(number_of_points=int(points_param))
            except ValueError:
                return Response(
                    {'detail': 'Parametr points musi być liczbą.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ids_param = request.query_params.get('ids')
        if ids_param:
            try:
                ids = [int(v) for v in ids_param.split(',') if v.strip() != '']
            except ValueError:
                return Response(
                    {'detail': 'Parametr ids musi być listą liczb oddzielonych przecinkami.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(id__in=ids)

        qs = qs.order_by('question_number')
        total = qs.count()

        try:
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            return Response(
                {'detail': 'Parametr offset musi być liczbą.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if offset < 0 or offset >= total:
            return Response({
                'category': category.symbol,
                'total': total,
                'offset': offset,
                'question': None,
            })

        question = qs[offset:offset + 1].first()
        return Response({
            'category': category.symbol,
            'total': total,
            'offset': offset,
            'question': QuestionSerializer(question).data,
        })