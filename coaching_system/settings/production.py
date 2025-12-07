from .base import *
import os
import dj_database_url

DEBUG = False

# Allow all hosts in Cloud Run (or restrict to specific domains)
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

# Cloud Run CSRF Trust
CSRF_TRUSTED_ORIGINS = ["https://*.run.app"]

# Database (Cloud SQL)
# Expects DATABASE_URL env var or individual connection params
DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )
}

# Static Files (WhiteNoise)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Google Cloud Storage for Media
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
