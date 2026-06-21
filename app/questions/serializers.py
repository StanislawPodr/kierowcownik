from rest_framework import serializers

from .models import Categories, ExamAttempt, Question

PASS_THRESHOLD = 68
EXAM_MAX_POINTS = 74
 
 
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


class ExamAttemptCreateSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=10)
    score = serializers.IntegerField(min_value=0)
    max_score = serializers.IntegerField(min_value=1)
    passed = serializers.BooleanField()

    def validate_category(self, value):
        symbol = value.strip()
        if not Categories.objects.filter(symbol__iexact=symbol).exists():
            raise serializers.ValidationError('Kategoria nie istnieje.')
        return symbol.upper()

    def validate(self, attrs):
        score = attrs['score']
        max_score = attrs['max_score']
        passed = attrs['passed']

        if score > max_score:
            raise serializers.ValidationError(
                {'score': 'Wynik nie może przekraczać maksymalnej liczby punktów.'},
            )

        expected_passed = score >= PASS_THRESHOLD
        if passed != expected_passed:
            raise serializers.ValidationError(
                {'passed': 'Pole passed jest niespójne z wynikiem.'},
            )

        return attrs

    def create(self, validated_data):
        category = Categories.objects.get(symbol__iexact=validated_data['category'])
        return ExamAttempt.objects.create(
            user=self.context['request'].user,
            category=category,
            score=validated_data['score'],
            max_score=validated_data['max_score'],
            passed=validated_data['passed'],
        )


class ExamAttemptSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.symbol', read_only=True)
    percent = serializers.SerializerMethodField()

    class Meta:
        model = ExamAttempt
        fields = (
            'id',
            'category',
            'score',
            'max_score',
            'passed',
            'percent',
            'created_at',
        )

    def get_percent(self, obj):
        return round((obj.score / EXAM_MAX_POINTS) * 100)

