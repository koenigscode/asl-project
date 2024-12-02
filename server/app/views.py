from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
from django.conf import settings
import random
import cv2
from django.views.decorators.csrf import csrf_exempt
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
    video_dir = os.path.join(settings.STATICFILES_DIRS[0], 'videos')
    video_files = [
        os.path.splitext(file)[0]
        for file in os.listdir(video_dir) if file.endswith(('.mp4', '.webm', '.ogg'))
    ]
    return render(request, 'app/study.html', {'word': random.choice(video_files)})


@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']

        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            tmp_file.write(video_file.read())
            tmp_file_path = tmp_file.name

        cap = cv2.VideoCapture(tmp_file_path)

        if not cap.isOpened():
            return JsonResponse({'error': 'Cant open video recording'}, status=400)

        ret, frame = cap.read()
        if not ret:
            cap.release()
            return JsonResponse({'error': 'Cant read video frame'}, status=400)

        # TODO: run inference on video

        result = "Well, this is a placeholder. But it means the server received the video! You might have signed it correctly!"

        cap.release()

        return JsonResponse({'result': result})

    return JsonResponse({'error': 'Invalid request, no video found'}, status=400)
