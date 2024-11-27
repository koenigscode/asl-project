FROM python:3.11-slim

WORKDIR /app

RUN pip install django

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
