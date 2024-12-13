# Use the official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Django will run on
EXPOSE 8001

# Default command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
