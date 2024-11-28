from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello ASL learner! This is our landing page!")
