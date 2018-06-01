from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from markdown import markdown


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    # __str__	⽅法是对象的字符串表示形式。我们使用板块的名称来表示它。
    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    # auto_now_add设置为True。这将告诉Django创建Post对象时为当前⽇期和时间。
    last_updated = models.DateTimeField(auto_now_add=True)
    # related_name是可选项。如果我们不为它设置⼀个名称，Django会⾃动⽣成它：(class_name)_set。
    # 例如，在Board模型中，所有Topic列表将⽤topic_set属性表示。
    # ⽽这⾥我们将其重新命名为了topics，以使其感觉更⾃然。
    board = models.ForeignKey(Board, related_name='topics')  # board用于指定它属于哪个版块。
    starter = models.ForeignKey(User, related_name='topics')  # starter用于识别谁发起的话题。
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    # 该ForeignKey字段需要⼀个位置参数related_name，⽤于引⽤它关联的模型。
    # 例如created_by是外键字段，关联的User模型，表明这个帖⼦是谁创建的，
    # related_name=posts表示在User那边可以使⽤user.posts来查看这个⽤户创建了哪些帖⼦
    created_by = models.ForeignKey(User, related_name='posts')
    # 该updated_by字段设置related_name='+'。这指示Django我们不需要这种反向关系，所以它会被忽略。
    updated_by = models.ForeignKey(User, null=True, related_name='+')

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))
