from django.test import TestCase
from django.urls import reverse, resolve

from boards.models import Board
from boards.views import board_topics

from boards.views import TopicListView


class BoardTopicsTests(TestCase):
    # Django 的测试机制不会针对当前数据库跑你的测试。
    def setUp(self):
        Board.objects.create(name='Django', description='Django board')

    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        # FBV
        # self.assertEquals(view.func, board_topics)
        # GCBV
        self.assertEquals(view.func.view_class, TopicListView)

    '''
    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
'''

    def test_board_topics_view_contains_navigation_link(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))
        self.assertContains(response, 'href="{0}"'.format(homepage_url))