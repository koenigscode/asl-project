"""
File: urls.py
Description: Code that defines the url paths.

Contributors:
Michael Koenig
Sofia Serbina

Created: 2024-11-27
Last Modified: 2024-12-29

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

from django.urls import path

from . import views

# Define the URL patterns for the app
urlpatterns = [
    path("", views.index, name="index"),
    path("browse/", views.browse, name="browse"),
    path("study/", views.study, name="study"),
    path("upload-video/", views.upload_video, name="upload_video")
]
