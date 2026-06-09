from rest_framework import serializers
from .models import Question, Categories
 
 
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = (
            'id', 
            'symbol'
         )
 
 
class QuestionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
 
    class Meta:
        model = Question
        fields = (
            'id',
            'question_number',
            'question_text',
            'is_basic',
            'answer_A',
            'answer_B',
            'answer_C',
            'correct_answer',
            'media_url',
            'url_type',
            'number_of_points',
            'category',
        )
 
