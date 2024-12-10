from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("browse/", views.browse, name="browse"),
    path("study/", views.study, name="study"),
    path("upload-video/", views.upload_video, name="upload_video")
]
