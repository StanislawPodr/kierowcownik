from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Categories(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    __str__ = lambda self: self.symbol


class Question(models.Model):
    class Answer(models.TextChoices):
        A = 'A', _('a')
        B = 'B', _('b')
        C = 'C', _('c')
        TRUE = 'T', _('True')
        FALSE = 'F', _('False')

    class UrlType(models.TextChoices):
        photo = 'P', _('photo')
        video = 'V', _('video')

    question_number = models.IntegerField(unique=True)
    question_text = models.TextField(max_length=500)
    is_basic = models.BooleanField(default=True)
    answer_A = models.TextField(max_length=500, blank=True, default='')
    answer_B = models.TextField(max_length=500, blank=True, default='')
    answer_C = models.TextField(max_length=500, blank=True, default='')
    correct_answer = models.CharField(max_length=1, choices=Answer.choices)
    media_url = models.URLField(max_length=500, blank=True, default='')
    url_type = models.CharField(max_length=1, choices=UrlType.choices, blank=True, default='')
    number_of_points = models.IntegerField(default=0)
    category = models.ManyToManyField(Categories)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    __str__ = lambda self: self.question_text


from django.conf import settings

class UserProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    wrong_questions = models.JSONField(default=list, blank=True)
    marked_questions = models.JSONField(default=list, blank=True)
    seen_questions = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress of {self.user.username}"

