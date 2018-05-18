from django.test import TestCase

# Create your tests here.
from django.urls import resolve, reverse

from boards.models import Board
from .views import home, board_topics


class HomeTests(TestCase):
    def test_home_view_status_code(self):
        # reverse的第一个参数是urls.py的url中的name
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        #
        view = resolve('/')
        self.assertEquals(view.url_name, 'home')
        self.assertEquals(view.func, home)


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
        self.assertEquals(view.func, board_topics)
