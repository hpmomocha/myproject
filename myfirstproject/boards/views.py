from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .models import Board


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
    return render(request, 'topics.html', {'board': board})
