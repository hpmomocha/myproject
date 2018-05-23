from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

'''
此测试⽤例抓取应⽤程序发送的电⼦邮件，并检查主题⾏，正⽂内容以及发送给谁。
'''


class PasswordResetMailTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.response = self.client.post(reverse('password_reset'), {'email': 'john@doe.com'})
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEquals('[Django Boards] Please reset your password', self.email.subject)

    def test_email_body(self):
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('password_reset_confirm', kwargs={
            'token': token,
            'uidb64': uid
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('john', self.email.body)
        self.assertIn('john@doe.com', self.email.body)

    def test_mail_to(self):
        self.assertEquals(['john@doe.com', ], self.email.to)
