from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from questions.models import Question, Categories

User = get_user_model()

MINUTES = 25

class ExamSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions', null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='exam_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=MINUTES)                                  # stały czas trwania egzaminu
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

class ExamSessionQuestion(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='session_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=2, blank=True, default='')
    is_answered = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('session', 'question')


    @property
    def is_correct(self):
        return self.selected_answer == self.question.correct_answer
 
