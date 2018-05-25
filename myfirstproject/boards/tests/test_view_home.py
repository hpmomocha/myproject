from django.test import TestCase
from django.urls import reverse, resolve

from boards.models import Board
from boards.views import home


class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django Board.')
        # reverse的第一个参数是urls.py的url中的name
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        #
        view = resolve('/')
        self.assertEquals(view.url_name, 'home')
        self.assertEquals(view.func, home)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        # assertContains ⽅法来测试 response 主体部分是否包含给定的⽂本。
        # 测试 response 主体是否包含⽂本 href="/boards/1/"
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))