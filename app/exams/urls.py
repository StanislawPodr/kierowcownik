from django.urls import path
from .views import StartExamView, SubmitAnswerView, ResumeExamView

urlpatterns = [
    path('start/<str:symbol>/', StartExamView.as_view(), name='exam-start'),
    path('<int:session_id>/answer/', SubmitAnswerView.as_view(), name='exam-answer'),
    path('<int:session_id>/resume/', ResumeExamView.as_view(), name='exam-resume'),
]