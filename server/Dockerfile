FROM public.ecr.aws/lts/ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv

RUN /venv/bin/pip install --upgrade pip
RUN /venv/bin/pip install django opencv-python-headless tensorflow mediapipe python-dotenv whitenoise moviepy stopwatch.py

VOLUME /app
VOLUME /models
VOLUME /recordings
VOLUME /tmp

WORKDIR /server

ENV MODEL_NAME=draft_model
ENV SAVE_RECORDINGS=True
ENV DEBUG=True

COPY . .

RUN /venv/bin/python3 manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/venv/bin/python3", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
