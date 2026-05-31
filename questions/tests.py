# questions/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Question, Answer, Tag, Vote
from users.models import UserProfile


class QuestionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test1234')
        UserProfile.objects.create(user=self.user)

    def test_create_question(self):
        q = Question.objects.create(
            author=self.user,
            title='How do I use Django?',
            body='Please explain Django to me.'
        )
        self.assertEqual(str(q), 'How do I use Django?')
        self.assertEqual(q.vote_score, 0)
        self.assertEqual(q.answer_count, 0)

    def test_create_tag_slug(self):
        tag = Tag.objects.create(name='Python Django')
        self.assertEqual(tag.slug, 'python-django')

    def test_create_answer(self):
        q = Question.objects.create(author=self.user, title='Test?', body='Test body')
        a = Answer.objects.create(author=self.user, question=q, body='Test answer')
        self.assertFalse(a.is_accepted)
        self.assertEqual(a.vote_score, 0)


class QuestionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username='testuser', password='test1234')
        UserProfile.objects.create(user=self.user)
        self.question = Question.objects.create(
            author=self.user,
            title='Test question',
            body='Test body'
        )

    def test_question_list_loads(self):
        response = self.client.get(reverse('question_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test question')

    def test_question_detail_loads(self):
        response = self.client.get(reverse('question_detail', args=[self.question.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test question')

    def test_ask_question_requires_login(self):
        response = self.client.get(reverse('ask_question'))
        # should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response['Location'])

    def test_logged_in_user_can_ask(self):
        self.client.login(username='testuser', password='test1234')
        response = self.client.post(reverse('ask_question'), {
            'title': 'My new question',
            'body' : 'Question body here',
            'tags' : 'python, django'
        })
        # should redirect to detail page after posting
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Question.objects.filter(title='My new question').exists())

    def test_vote_own_post_rejected(self):
        self.client.login(username='testuser', password='test1234')
        response = self.client.get(reverse('vote', args=['question', self.question.pk, 1]))
        data = response.json()
        self.assertIn('error', data)