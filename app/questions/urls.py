from django.urls import path

from .views import CategoryExamView, CategoryListView

urlpatterns = [
    path('exam/category/<str:symbol>/', CategoryExamView.as_view(), name='exam-category'),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
]