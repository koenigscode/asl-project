from django.http import JsonResponse
import mimetypes
from django.shortcuts import render
import os
from django.conf import settings
import random
from django.views.decorators.csrf import csrf_exempt
from .prediction import predict
import tempfile

# View function for the index page
def index(request):
    return render(request, 'app/index.html')

# View function for browsing available videos
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

# View function for the study page
def study(request):
    WORDS = os.getenv('WORDS')
    if WORDS is None:
        raise ValueError("Environment variable 'WORDS' is not set.")
    words = WORDS.split(',')

    # don't show same word two times in a row
    last_word = request.GET.get('last_word')
    if last_word in words:
        words.remove(last_word)

    word = random.choice(words)
    instruction_video = f"videos/{word}.mp4"

    return render(request, 'app/study.html', {'word': word, 'instruction_video': instruction_video})

# View function for uploading a video
@csrf_exempt
def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        word = request.POST.get('word')

        # Check if the uploaded file is a valid video
        mime_type, _ = mimetypes.guess_type(video_file.name)
        if mime_type is None or not mime_type.startswith('video/'):
            return JsonResponse({'error': 'Invalid recording format'}, status=400)

        file_ext = mimetypes.guess_extension(mime_type)
        if file_ext is None:
            return JsonResponse({'error': "Can't detect file extension for recording"}, status=400)

        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix=file_ext) as tmp_file:
            tmp_file.write(video_file.read())
            tmp_file_path = tmp_file.name
            prediction = predict(tmp_file_path, word)

        # Check the prediction result
        if prediction is None:
            return JsonResponse({'error': "Couldn't detect any hand movement"}, status=400)
        elif prediction[0] is None:
            return JsonResponse({'error': "Couldn't detect any sign"}, status=400)
        elif prediction[0] == word:
            result = "Correctly signed!"
        else:
            result = f"Wrong sign! We thought you signed {prediction[0]}."

        return JsonResponse({'result': result})

    return JsonResponse({'error': 'Invalid request, no video found'}, status=400)
