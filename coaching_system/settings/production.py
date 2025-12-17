from .base import *
import os
import dj_database_url

DEBUG = False

# ---- HOSTS & CSRF ----
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split()
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split()

# ---- DATABASE (NO DUMMY FALLBACK IN PROD) ----
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in production")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )
}

# ---- STATIC FILES (WhiteNoise ONLY) ----
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ---- MEDIA FILES (GCS ONLY) ----
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
if not GS_BUCKET_NAME:
    raise RuntimeError("GS_BUCKET_NAME is not set")

STORAGES = {
    # MEDIA files → Google Cloud Storage
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "bucket_name": GS_BUCKET_NAME,
        },
    },

    # STATIC files → WhiteNoise
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

# ---- PROXY / HTTPS (Cloud Run) ----
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ---- SECURITY ----
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
