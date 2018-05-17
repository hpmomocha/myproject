from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# 视图是接收httprequest对象并返回⼀个httpresponse对象的Python函数。
def home(request):
	return HttpResponse('Hello, World!')