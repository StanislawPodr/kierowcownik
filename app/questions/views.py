from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Categories, Question
from .serializers import QuestionSerializer

from utils import _generate_exam_questions


class CategoryExamView(APIView):
    """
    GET /api/questions/exam/category/<symbol>/

    Zwraca losowy test z podanej kategorii:
    20 pytań podstawowych + 12 specjalistycznych
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, symbol):
        category = get_object_or_404(Categories, symbol__iexact=symbol)

        all_questions = _generate_exam_questions(category)

        return Response({
            'category': category.symbol,
            'basic_count': len([q for q in all_questions if q.is_basic]),
            'specialist_count': len([q for q in all_questions if not q.is_basic]),
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