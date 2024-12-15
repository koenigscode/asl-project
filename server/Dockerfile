FROM python:3.11-alpine


WORKDIR /server

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 ffmpeg

RUN pip install django opencv-python-headless tensorflow mediapipe python-dotenv whitenoise moviepy stopwatch.py gunicorn
ENV MODEL_NAME=draft_model
ENV SAVE_RECORDINGS=True
ENV DEBUG=True

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
