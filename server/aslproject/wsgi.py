"""
File: wsgi.py
Description: WSGI config for aslproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/

Contributors:
Sofia Serbina

Created: 2024-11-27
Last Modified: 2024-11-27

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aslproject.settings')

application = get_wsgi_application()
