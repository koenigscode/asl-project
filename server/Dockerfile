FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install django opencv-python-headless tensorflow mediapipe python-dotenv whitenoise tqdm scikit-learn TIME-python

# Copy all files from the current directory to the container
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/server \
    MAX_FRAMES=47 \
    NUM_FEATURES=126 \
    WORDS=no,eat,teacher,want,fish \
    FPS=20

# Collect static files for Django
RUN python manage.py collectstatic --noinput

# Expose the application's port
EXPOSE 8000

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]