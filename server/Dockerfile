FROM public.ecr.aws/lts/ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install django opencv-python-headless tensorflow mediapipe python-dotenv whitenoise moviepy stopwatch.py gunicorn

WORKDIR /server

COPY . .

RUN python3 manage.py collectstatic --noinput

RUN python3 manage.py migrate

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
