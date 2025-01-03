"""
File: apps.py
Description: configuration file

Contributors:
Sofia Serbina

Created: 2024-11-27
Last Modified: 2024-11-27

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
