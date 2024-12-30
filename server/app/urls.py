from django.urls import path

from . import views

# Define the URL patterns for the app
urlpatterns = [
    path("", views.index, name="index"),
    path("browse/", views.browse, name="browse"),
    path("study/", views.study, name="study"),
    path("upload-video/", views.upload_video, name="upload_video")
]
