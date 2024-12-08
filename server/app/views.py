from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
from django.conf import settings
import random
import cv2
from django.views.decorators.csrf import csrf_exempt
from .prediction import predict
import tempfile


def index(request):
    return render(request, 'app/index.html')


def browse(request):
    video_dir = os.path.join(settings.STATICFILES_DIRS[0], 'videos')
    video_files = [
        {
            'path': f"videos/{file}",
            'name': os.path.splitext(file)[0]
        }
        for file in os.listdir(video_dir) if file.endswith(('.mp4', '.webm', '.ogg'))
    ]
    return render(request, 'app/browse.html', {'video_files': video_files})


def study(request):
    WORDS = os.getenv('WORDS')
    if WORDS is None:
        raise ValueError("Environment variable 'WORDS' is not set.")
    words = WORDS.split(',')


    return render(request, 'app/study.html', {'word': random.choice(words)})


@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        word = request.POST.get('word')

        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp4') as tmp_file:
            tmp_file.write(video_file.read())
            tmp_file_path = tmp_file.name
            prediction = predict(tmp_file_path)

        if prediction is None:
            return JsonResponse({'error': "Couldn't detect any hand movement"}, status=400)
        elif prediction[0] == word:
            result = "Correctly signed!"
        else:
            result = f"Wrong sign! We thought you signed {prediction[0]}."

        return JsonResponse({'result': result})

    return JsonResponse({'error': 'Invalid request, no video found'}, status=400)
