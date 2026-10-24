"""WSGI config for Akash Art Space."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "akash_art_space.settings")
application = get_wsgi_application()
