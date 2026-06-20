from django.urls import path


from .views import (
    CategoryExamView,
    CategoryListView,
    WordExamView,
    AllQuestionsView,
    RandomQuestionsView,
    CategoryQuestionsMetaView, 
    CategoryQuestionSequentialView, 
    CategoryQuestionsView,
    UserProgressView
)

urlpatterns = [
    path("exam/word/", WordExamView.as_view(), name="exam-word"),
    path(
        "exam/category/<str:symbol>/",
        CategoryExamView.as_view(),
        name="exam-category",
    ),
    path("categories/", CategoryListView.as_view(), name="categories-list"),
    path(
        "all/<str:category>/",
        AllQuestionsView.as_view(),
        name="all-questions",
    ),
    path(
        "random/<str:category>/",
        RandomQuestionsView.as_view(),
        name="random-question",
    ),
    path('category/<str:symbol>/meta/', CategoryQuestionsMetaView.as_view()),
    path('category/<str:symbol>/sequential/', CategoryQuestionSequentialView.as_view()),
    path('category/<str:symbol>/', CategoryQuestionsView.as_view()),
    path('progress/', UserProgressView.as_view(), name='user-progress'),
]
