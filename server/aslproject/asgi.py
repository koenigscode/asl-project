"""
File: asgi.py
Description: ASGI config for aslproject project.
It exposes the ASGI callable as a module-level variable named ``application``.

Contributors:
Sofia Serbina

Created: 2024-11-27
Last Modified: 2024-11-27

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aslproject.settings')

application = get_asgi_application()
