
from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name, default=False):
    return (
        os.environ.get(name, str(default))
        .strip()
        .lower()
        in {"1", "true", "yes", "on"}
    )


# --------------------------------------------------
# SECURITY AND ENVIRONMENT SETTINGS
# --------------------------------------------------

DEBUG = _env_bool("DJANGO_DEBUG", True)

_configured_secret_key = os.environ.get("DJANGO_SECRET_KEY", "").strip()
_configured_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "").strip()

if not DEBUG and not _configured_secret_key:
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY when DEBUG is disabled."
    )

if not DEBUG and not _configured_hosts:
    raise ImproperlyConfigured(
        "Set DJANGO_ALLOWED_HOSTS when DEBUG is disabled."
    )

SECRET_KEY = (
    _configured_secret_key
    or "dev-only-change-this-key-before-deployment"
)

ALLOWED_HOSTS = [
    host.strip()
    for host in (_configured_hosts or "localhost,127.0.0.1").split(",")
    if host.strip()
]

SECURE_SSL_REDIRECT = _env_bool(
    "DJANGO_SECURE_SSL_REDIRECT", not DEBUG
)

# Render terminates HTTPS at its edge proxy and forwards the original scheme
# in this header. Trust it so Django does not redirect HTTPS requests again.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = int(
    os.environ.get(
        "DJANGO_SECURE_HSTS_SECONDS",
        "31536000" if not DEBUG else "0",
    )
)

SESSION_COOKIE_SECURE = _env_bool(
    "DJANGO_SESSION_COOKIE_SECURE", not DEBUG
)

CSRF_COOKIE_SECURE = _env_bool(
    "DJANGO_CSRF_COOKIE_SECURE", not DEBUG
)


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main.apps.MainConfig",
]


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# URLS AND TEMPLATES
# --------------------------------------------------

ROOT_URLCONF = "akash_art_space.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "template"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "akash_art_space.wsgi.application"
ASGI_APPLICATION = "akash_art_space.asgi.application"


# --------------------------------------------------
# DATABASE
# SQLite locally; PostgreSQL when DATABASE_URL is set.
# --------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    try:
        import dj_database_url
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Install dj-database-url to use DATABASE_URL."
        ) from exc

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True


# --------------------------------------------------
# STATIC AND MEDIA FILES
# --------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "Static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media")))


# --------------------------------------------------
# DEFAULTS AND EMAIL
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "webmaster@localhost",
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
