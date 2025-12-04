from pathlib import Path
import os
import dj_database_url
from google.auth import compute_engine

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_in_production")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # local apps
    'core',
    'students',
    'batches',
    'attendance',
    'materials',
    'exams',
    'assignments',
    'fees',
    'enquiries',

    # Google Cloud Storage
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'coaching_system.urls'
WSGI_APPLICATION = 'coaching_system.wsgi.application'
ASGI_APPLICATION = 'coaching_system.asgi.application'

# DATABASE
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR/'db.sqlite3'}"),
        conn_max_age=600
    )
}

# STATIC FILES
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# GOOGLE CLOUD STORAGE MEDIA
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
GS_CREDENTIALS = compute_engine.Credentials()
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
