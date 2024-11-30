from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'app/index.html')

def browse(request):
    return render(request, 'app/browse.html')

def study(request):
    return render(request, 'app/study.html')
