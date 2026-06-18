import json
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from questions.models import Categories, Question
from questions.serializers import QuestionSerializer
from .models import ExamSession, ExamSessionQuestion
from .utils import generate_exam_cookie_data


MINUTES = 25
COOKIE_NAME = 'kierowcownik_exam_state'

class StartExamView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, symbol):
        category = get_object_or_404(Categories, symbol__iexact=symbol)
        
        user = request.user if request.user.is_authenticated else None
        session = ExamSession.objects.create(user=user, category=category)
        
        base_qs = Question.objects.filter(category=category)
        basic_qs = base_qs.filter(is_basic=True).order_by('?')[:20]
        specialist_qs = base_qs.filter(is_basic=False).order_by('?')[:12]
        all_questions = list(basic_qs) + list(specialist_qs)
        
        exam_questions = [
            ExamSessionQuestion(session=session, question=q, order=index)
            for index, q in enumerate(all_questions)
        ]
        ExamSessionQuestion.objects.bulk_create(exam_questions)
        
        cookie_data = generate_exam_cookie_data(session, request)
        
        response_data = {
            'session_id': session.id,
            'category': category.symbol,
            'ends_at': cookie_data['ends_at'],
            'questions': QuestionSerializer(all_questions, many=True).data
        }
        
        response = Response(response_data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            key=COOKIE_NAME,
            value=json.dumps(cookie_data),
            max_age=MINUTES * 60,  
            samesite='Lax',
            secure=False,     
            httponly=False    
        )
        return response


class SubmitAnswerView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, session_id):
        session = get_object_or_404(ExamSession, id=session_id, is_completed=False)
        
        if session.is_expired:
            session.is_completed = True
            session.save()
            return Response({'detail': 'Czas egzaminu minął.'}, status=status.HTTP_400_BAD_REQUEST)
            
        question_id = request.data.get('question_id')
        answer = request.data.get('answer')  # możliwe wartości: A, B, C, T, F
        
        session_question = get_object_or_404(ExamSessionQuestion, session=session, question_id=question_id)
        session_question.selected_answer = answer
        session_question.is_answered = True
        session_question.save()
        
        cookie_data = generate_exam_cookie_data(session, request)
        remaining_seconds = max(0, int(session.expires_at.timestamp() - timezone.now().timestamp()))
        
        response = Response({
            'detail': 'Odpowiedź zapisana pomyślnie.',
            'cookie_cache': cookie_data
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key=COOKIE_NAME,
            value=json.dumps(cookie_data),
            max_age=remaining_seconds,
            samesite='Lax',
            secure=False,
            httponly=False
        )
        return response


class ResumeExamView(APIView):
    """
    Wywoływany przez frontend po odświeżeniu strony, jeśli wykryto aktywny cookie egzaminu.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, session_id):
        session = get_object_or_404(ExamSession, id=session_id)
        
        if session.is_expired or session.is_completed:
            session.is_completed = True
            session.save()
            response = Response({'detail': 'Egzamin zakończył się lub wygasł.'}, status=status.HTTP_400_BAD_REQUEST)
            response.delete_cookie(COOKIE_NAME)
            return response
            
        session_questions = session.session_questions.all().select_related('question')
        
        questions_data = []
        for sq in session_questions:
            data = QuestionSerializer(sq.question).data
            data['user_answer'] = sq.selected_answer
            data['is_answered'] = sq.is_answered
            questions_data.append(data)
            
        cookie_data = generate_exam_cookie_data(session, request)
        remaining_seconds = max(0, int(session.expires_at.timestamp() - timezone.now().timestamp()))
        
        response = Response({
            'session_id': session.id,
            'category': session.category.symbol,
            'ends_at': cookie_data['ends_at'],
            'questions': questions_data
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key=COOKIE_NAME,
            value=json.dumps(cookie_data),
            max_age=remaining_seconds,
            samesite='Lax',
            secure=False,
            httponly=False
        )
        return response
