from django.shortcuts import render
from django.http import HttpResponse

from .models import Board


# Create your views here.
# 视图是接收httprequest对象并返回⼀个httpresponse对象的Python函数。
def home(request):
    boards = Board.objects.all()

    return render(request, 'home.html', {'boards': boards})
