from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Categories, ExamAttempt, Question, UserProgress
from .serializers import (
    EXAM_MAX_POINTS,
    ExamAttemptCreateSerializer,
    ExamAttemptSerializer,
    QuestionSerializer,
)
from .utils import _generate_exam_questions


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

        all_questions = _generate_exam_questions(category_b)

        return Response({
            'category': 'B',
            'basic_count': len([q for q in all_questions if q.is_basic]),
            'specialist_count': len([q for q in all_questions if not q.is_basic]),
            'total': len(all_questions),
            'questions': QuestionSerializer(all_questions, many=True).data,
        })


class CategoryExamView(APIView):
    """
    GET /api/questions/exam/category/<symbol>/

    Zwraca losowy test z podanej kategorii:
    20 pytań podstawowych + 12 specjalistycznych zgodnie ze strukturą punktową WORD.
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

        # Retrieve query parameters
        ids = None
        ids_param = request.query_params.get('ids')
        if ids_param:
            try:
                ids = [int(v) for v in ids_param.split(',') if v.strip() != '']
            except ValueError:
                return Response(
                    {'detail': 'Parametr ids musi być listą liczb.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        exclude_ids = []
        exclude_ids_param = request.query_params.get('exclude_ids')
        if exclude_ids_param:
            try:
                exclude_ids = [int(v) for v in exclude_ids_param.split(',') if v.strip() != '']
            except ValueError:
                return Response(
                    {'detail': 'Parametr exclude_ids musi być listą liczb.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        status_filter = request.query_params.get('status_filter')

        # If authenticated, merge with database records
        if request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user)
                
                db_ids = None
                if status_filter == 'markedOnly':
                    db_ids = progress.marked_questions
                elif status_filter == 'wrongOnly':
                    db_ids = progress.wrong_questions
                
                if db_ids is not None:
                    if ids is not None:
                        ids = list(set(ids + db_ids))
                    else:
                        ids = db_ids
                
                if status_filter != 'markedOnly' and status_filter != 'wrongOnly':
                    exclude_ids = list(set(exclude_ids + progress.seen_questions))
            except UserProgress.DoesNotExist:
                pass

        if ids is not None:
            qs = qs.filter(id__in=ids)

        qs = qs.order_by('question_number')
        total = qs.count()

        # Calculate unseen count and offsets on IDs list (extremely fast)
        ids_list = list(qs.values_list('id', flat=True))
        exclude_ids_set = set(exclude_ids)
        unseen_ids = [q_id for q_id in ids_list if q_id not in exclude_ids_set]
        unseen_total = len(unseen_ids)

        first_unseen_offset = 0
        for idx, q_id in enumerate(ids_list):
            if q_id not in exclude_ids_set:
                first_unseen_offset = idx
                break

        try:
            offset = int(request.query_params.get('offset', -1))
        except ValueError:
            return Response(
                {'detail': 'Parametr offset musi być liczbą.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if offset == -1:
            offset = first_unseen_offset

        if offset < 0 or (total > 0 and offset >= total):
            return Response({
                'category': category.symbol,
                'total': total,
                'unseen_total': unseen_total,
                'offset': offset,
                'first_unseen_offset': first_unseen_offset,
                'next_unseen_offset': None,
                'question': None,
            })

        if total == 0:
            return Response({
                'category': category.symbol,
                'total': total,
                'unseen_total': unseen_total,
                'offset': offset,
                'first_unseen_offset': first_unseen_offset,
                'next_unseen_offset': None,
                'question': None,
            })

        # Calculate the next unseen offset starting from offset + 1
        next_unseen_offset = None
        for idx in range(offset + 1, len(ids_list)):
            if ids_list[idx] not in exclude_ids_set:
                next_unseen_offset = idx
                break

        question = qs[offset:offset + 1].first()
        return Response({
            'category': category.symbol,
            'total': total,
            'unseen_total': unseen_total,
            'offset': offset,
            'first_unseen_offset': first_unseen_offset,
            'next_unseen_offset': next_unseen_offset,
            'question': QuestionSerializer(question).data,
        })


class AllQuestionsView(APIView):
    """
    GET /api/questions/all/<str:category>/
    
    Zwraca listę wszystkich pytań
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, category):
        try:
            category = Categories.objects.get(symbol__iexact=category)
        except Categories.DoesNotExist:
            return Response(
                {'detail': f'Kategoria {category} nie istnieje w bazie danych.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        all_questions = Question.objects.filter(category=category)
        no_basic_questions = len(list(all_questions.filter(is_basic=True)))
        no_specialist_questions = len(list(all_questions.filter(is_basic=False)))
        return Response({
            'category': 'all',
            'basic_count': no_basic_questions,
            'specialist_count': no_specialist_questions,
            'total': no_basic_questions + no_specialist_questions,
            'questions': QuestionSerializer(list(all_questions), many=True).data,
        })

class RandomQuestionsView(APIView):
    """
    GET /api/questions/random/<str:category>/
    
    Zwraca listę wszystkich pytań
    """

    permission_classes = (permissions.AllowAny,)

    def get(self, request, category):
        try:
            category = Categories.objects.get(symbol__iexact=category)
        except Categories.DoesNotExist:
            return Response(
                {'detail': f'Kategoria {category} nie istnieje w bazie danych.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        all_questions = Question.objects.filter(category=category)
        sample_question = _sample_questions(all_questions, 1)
        no_basic_questions = len(list(sample_question.filter(is_basic=True)))
        no_specialist_questions = len(list(sample_question.filter(is_basic=False)))
        return Response({
            'category': 'all',
            'basic_count': no_basic_questions,
            'specialist_count': no_specialist_questions,
            'total': 1,
            'questions': QuestionSerializer(sample_question.first()).data,
        })


class UserProgressView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        progress, created = UserProgress.objects.get_or_create(user=request.user)
        return Response({
            'wrong_questions': progress.wrong_questions,
            'marked_questions': progress.marked_questions,
            'seen_questions': progress.seen_questions,
        })

    def post(self, request):
        progress, created = UserProgress.objects.get_or_create(user=request.user)

        wrong = request.data.get('wrong_questions')
        marked = request.data.get('marked_questions')
        seen = request.data.get('seen_questions')

        if wrong is not None:
            if not isinstance(wrong, list):
                return Response({'detail': 'wrong_questions must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                progress.wrong_questions = list(set(int(x) for x in wrong))
            except (ValueError, TypeError):
                return Response({'detail': 'wrong_questions contains invalid IDs'}, status=status.HTTP_400_BAD_REQUEST)

        if marked is not None:
            if not isinstance(marked, list):
                return Response({'detail': 'marked_questions must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                progress.marked_questions = list(set(int(x) for x in marked))
            except (ValueError, TypeError):
                return Response({'detail': 'marked_questions contains invalid IDs'}, status=status.HTTP_400_BAD_REQUEST)

        if seen is not None:
            if not isinstance(seen, list):
                return Response({'detail': 'seen_questions must be a list'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                progress.seen_questions = list(set(int(x) for x in seen))
            except (ValueError, TypeError):
                return Response({'detail': 'seen_questions contains invalid IDs'}, status=status.HTTP_400_BAD_REQUEST)

        progress.save()
        return Response({
            'wrong_questions': progress.wrong_questions,
            'marked_questions': progress.marked_questions,
            'seen_questions': progress.seen_questions,
        })


class ExamAttemptListCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        qs = ExamAttempt.objects.filter(user=request.user).select_related('category')
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category__symbol__iexact=category.strip())
        serializer = ExamAttemptSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExamAttemptCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        attempt = serializer.save()
        return Response(
            ExamAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )


class ExamAttemptStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        qs = ExamAttempt.objects.filter(user=request.user)
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category__symbol__iexact=category.strip())
        agg = qs.aggregate(
            total_attempts=Count('id'),
            passed_count=Count('id', filter=Q(passed=True)),
            avg_score=Avg('score'),
        )
        last = qs.select_related('category').first()
        total = agg['total_attempts'] or 0
        passed = agg['passed_count'] or 0
        avg_score = agg['avg_score']
        avg_score_rounded = round(avg_score, 1) if avg_score is not None else 0
        avg_percent = round((avg_score / EXAM_MAX_POINTS) * 100) if avg_score is not None else 0
        return Response({
            'total_attempts': total,
            'passed_count': passed,
            'pass_rate': round((passed / total) * 100) if total else 0,
            'avg_score': avg_score_rounded,
            'avg_percent': avg_percent,
            'last_attempt': ExamAttemptSerializer(last).data if last else None,
        })

