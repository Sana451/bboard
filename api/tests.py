from rest_framework.test import APIClient

from api.serializers import BbSerializer, CommentSerializer
from main.models import AdvUser, Bb, Rubric, Comment, BbScores

client = APIClient()
client.post('/notes/', {'title': 'new idea'}, format='json')

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class BboardApiTests(APITestCase):
    def setUp(self):
        self.user = AdvUser.objects.create_user(username='TestUser1', password='qwerty')
        self.client.force_login(self.user)
        self.super_ribric1 = Rubric.objects.create(name='Test SuperRubric 1')
        self.ribric1 = Rubric.objects.create(name='Test Rubric 1', super_rubric=self.super_ribric1)
        self.ribric2 = Rubric.objects.create(name='Test Rubric 2', super_rubric=self.super_ribric1)
        for i in range(11):
            Bb.objects.create(rubric=self.ribric1, title=f'bb {i}', content=f'content bb {i}', price=10 + i,
                              contacts=f'892103101{i}', author=self.user)
        self.bb1 = Bb.objects.all()[0]
        for i in range(5):
            Comment.objects.create(bb=self.bb1, author=self.user, content=f'comment {i}',
                                   score=BbScores.FIVE)

    def test_list_bbs(self):
        url = reverse('api:bbs-list')
        response = self.client.get(url, format='json')
        serializer = BbSerializer(response.data, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(response.data, serializer.data)

    def test_list_comments(self):
        comments = self.bb1.comment_set.all()
        url = reverse('api:bbs-detail-comments', kwargs={'pk': self.bb1.pk})
        response = self.client.get(url, format='json')
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data, serializer.data)

    def test_create_comment(self):
        url = reverse('api:bbs-detail-comments', kwargs={'pk': self.bb1.pk})
        data = {"author": "sana451", "content": "sasasas", "score": 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], data['author'])
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['score'], data['score'])
