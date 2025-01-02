FROM python:3.11-slim

# Set working directory for the container
WORKDIR /app

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 ffmpeg \
    libxext6 libxrender1 libxtst6 libxi6 libxkbcommon-x11-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install django opencv-python-headless tensorflow mediapipe python-dotenv whitenoise moviepy stopwatch.py tqdm scikit-learn TIME-python jupyter coverage

# Copy the current directory contents into the container at /app
COPY . .

# Collect static files for Django
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
