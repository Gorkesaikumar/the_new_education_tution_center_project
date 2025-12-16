from .base import *
import os
from urllib.parse import urlparse


DEBUG = False

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "shoebsiracademy.org,www.shoebsiracademy.org"
).split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://shoebsiracademy.org",
    "https://www.shoebsiracademy.org",
]

DATABASE_URL = os.getenv("DATABASE_URL")

# ---- DATABASE CONFIG ----
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Build-time safe dummy DB
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.dummy"
        }
    }

# ---- STATIC FILES ----
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---- MEDIA (GCS) ----
GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "bucket_name": GS_BUCKET_NAME,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

# ---- SECURITY ----
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
