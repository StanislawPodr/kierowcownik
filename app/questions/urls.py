from django.urls import path

from .views import CategoryExamView, CategoryListView, WordExamView, CategoryQuestionsMetaView, CategoryQuestionSequentialView, CategoryQuestionsView

urlpatterns = [
    path('exam/word/', WordExamView.as_view(), name='exam-word'),
    path('exam/category/<str:symbol>/', CategoryExamView.as_view(), name='exam-category'),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('category/<str:symbol>/meta/', CategoryQuestionsMetaView.as_view()),
    path('category/<str:symbol>/sequential/', CategoryQuestionSequentialView.as_view()),
    path('category/<str:symbol>/', CategoryQuestionsView.as_view())
]