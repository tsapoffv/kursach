"""
WSGI config for schedule_project project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_project.settings')

application = get_wsgi_application()