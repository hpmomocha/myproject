from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView

from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post


# Create your views here.
# 视图是接收httprequest对象并返回⼀个httpresponse对象的Python函数。
def home(request):
    boards = Board.objects.all()

    return render(request, 'home.html', {'boards': boards})


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics_GCBV.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)

        return queryset


def board_topics(request, pk):
    # 因为我们在urls.py里使⽤了 (?P<pk>\d+) 正则表达式
    '''try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404
    '''
    # Django 有⼀个快捷⽅式去得到⼀个对象，或者返回⼀个不存在的对象 404。
    board = get_object_or_404(Board, pk=pk)
    # topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    # 如果只是使用 request.GET['page'] 访问变量，在Get数据时 page 不可得,可能引发 KeyError .
    # 这里的 get() 是每个python的的字典数据类型都有的方法。
    # 使用的时候要小心：假设 request.GET 包含一个 'page' 的key是不安全的，
    # 所以我们使用 get('page', 1) 提供一个缺省的返回值1
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 20)

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)

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


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts_GCBV.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


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
