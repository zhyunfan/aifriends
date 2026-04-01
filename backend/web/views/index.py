from django.shortcuts import render


def index(request):
    return render(request, 'index.html')#是templates文件夹里面的文件