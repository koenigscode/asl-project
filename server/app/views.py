from django.http import HttpResponse
from django.shortcuts import render
import os
from django.conf import settings


def index(request):
    return render(request, 'app/index.html')


def browse(request):
    video_dir = os.path.join(settings.STATICFILES_DIRS[0], 'videos')
    # Get a list of video file names
    video_files = [
        {
            'path': f"videos/{file}",  # File path for the video
            'name': os.path.splitext(file)[0]  # File name without extension
        }
        for file in os.listdir(video_dir) if file.endswith(('.mp4', '.webm', '.ogg'))
    ]
    return render(request, 'app/browse.html', {'video_files': video_files})


def study(request):
    return render(request, 'app/study.html')
