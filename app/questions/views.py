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
    permission_classes = (permissions.IsAuthenticated,)

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
    permission_classes = (permissions.IsAuthenticated,)

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
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        from .serializers import CategorySerializer
        categories = Categories.objects.all().order_by('symbol')
        return Response({'categories': CategorySerializer(categories, many=True).data})