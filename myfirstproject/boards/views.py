from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post


# Create your views here.
# 视图是接收httprequest对象并返回⼀个httpresponse对象的Python函数。
def home(request):
    boards = Board.objects.all()

    return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
    # 因为我们在urls.py里使⽤了 (?P<pk>\d+) 正则表达式
    '''try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404
    '''
    # Django 有⼀个快捷⽅式去得到⼀个对象，或者返回⼀个不存在的对象 404。
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'topics.html', {'board': board, 'topics': topics})


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    # user = User.objects.first()
    user = request.user
    if request.method == 'POST':
        # 实例化⼀个将 POST 数据传递给 form 的form 实例：
        form = NewTopicForm(request.POST)
        # 检查 form 是否有效
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()

            post = Post.objects.create(message=form.cleaned_data.get('message'),
                                       topic=topic,
                                       created_by=user)
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()

    return render(request, 'topic_posts.html', {'topic': topic})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()

    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    # 使⽤ fields 属性来即时创建模型表单
    fields = ('message',)
    template_name = 'edit_post.html'
    # 系统将使⽤ pk_url_kwarg 来标识⽤于检索 Post 对象的关键字参数的名称
    # 此处不太明白，需要进一步学习。
    pk_url_kwarg = 'post_pk'
    # 如果我们没有设置 context_object_name 属性，Post 对象将作为“Object”在模板中可⽤。
    # 所以，在这⾥我们使⽤ context_object_name 来重命名它来发布
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
