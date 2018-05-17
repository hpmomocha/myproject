from django.test import TestCase

# Create your tests here.
from django.urls import resolve, reverse

from .views import home


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
