from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..views import topic_posts, PostListView
from ..models import Board, Topic, Post


class TopicPostsTests(TestCase):
    def setUp(self):
        board = Board.objects.create(name='Django', description='Django board')
        user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        topic = Topic.objects.create(subject='Hello, world', board=board, starter=user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=topic, created_by=user)
        url = reverse('topic_posts', kwargs={'topic_pk': topic.pk, 'pk': board.pk})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/')
        # FBV
        # self.assertEquals(view.func, topic_posts)
        # GCBV
        self.assertEquals(view.func.view_class, PostListView)