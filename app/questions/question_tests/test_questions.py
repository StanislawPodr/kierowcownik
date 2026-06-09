from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from questions.models import Categories, Question

User = get_user_model()

WORD_EXAM_URL = '/api/questions/exam/word/'
CATEGORY_LIST_URL = '/api/questions/categories/'


def category_exam_url(symbol):
    return f'/api/questions/exam/category/{symbol}/'


def make_question(number, is_basic, categories, points=1):
    q = Question.objects.create(
        question_number=number,
        question_text=f'Pytanie {number}',
        is_basic=is_basic,
        answer_A='Tak',
        answer_B='Nie',
        answer_C='Może',
        correct_answer='A',
        number_of_points=points,
    )
    q.category.set(categories)
    return q


class ExamEndpointsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='haslo12345')
        self.cat_b = Categories.objects.create(symbol='B')
        self.cat_a = Categories.objects.create(symbol='A')

        for i in range(1, 26):
            make_question(i, is_basic=True, categories=[self.cat_b])
        for i in range(26, 41):
            make_question(i, is_basic=False, categories=[self.cat_b])


        for i in range(100, 105):
            make_question(i, is_basic=True, categories=[self.cat_a])

        login = self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'haslo12345'},
            format='json',
        )
        self.token = login.data['access']
        self.auth = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}




    def test_word_exam_requires_auth(self):
        response = self.client.get(WORD_EXAM_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_word_exam_returns_correct_counts(self):
        response = self.client.get(WORD_EXAM_URL, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['basic_count'], 20)
        self.assertEqual(response.data['specialist_count'], 12)
        self.assertEqual(response.data['total'], 32)
        self.assertEqual(len(response.data['questions']), 32)

    def test_word_exam_no_duplicates(self):
        response = self.client.get(WORD_EXAM_URL, **self.auth)
        ids = [q['id'] for q in response.data['questions']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_word_exam_missing_category_b_returns_404(self):
        self.cat_b.delete()
        response = self.client.get(WORD_EXAM_URL, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)





    def test_category_exam_requires_auth(self):
        response = self.client.get(category_exam_url('B'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_exam_b_returns_correct_counts(self):
        response = self.client.get(category_exam_url('B'), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category'], 'B')
        self.assertEqual(response.data['basic_count'], 20)
        self.assertEqual(response.data['specialist_count'], 12)

    def test_category_exam_returns_fewer_if_not_enough_questions(self):
        response = self.client.get(category_exam_url('A'), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['basic_count'], 5)
        self.assertEqual(response.data['specialist_count'], 0)

    def test_category_exam_case_insensitive(self):
        response = self.client.get(category_exam_url('b'), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category'], 'B')

    def test_category_exam_unknown_category_returns_404(self):
        response = self.client.get(category_exam_url('Z'), **self.auth)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)





    def test_categories_list_requires_auth(self):
        response = self.client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_categories_list_returns_all(self):
        response = self.client.get(CATEGORY_LIST_URL, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        symbols = [c['symbol'] for c in response.data['categories']]
        self.assertIn('A', symbols)
        self.assertIn('B', symbols)