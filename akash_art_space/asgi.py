"""ASGI config for Akash Art Space."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "akash_art_space.settings")
application = get_asgi_application()
