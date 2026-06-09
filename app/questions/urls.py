from django.urls import path

from .views import CategoryExamView, CategoryListView, WordExamView

urlpatterns = [
    path('exam/word/', WordExamView.as_view(), name='exam-word'),
    path('exam/category/<str:symbol>/', CategoryExamView.as_view(), name='exam-category'),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
]