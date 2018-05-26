from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect

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
