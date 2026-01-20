from .base import *
import os


DEBUG = False

# -------------------------------------------------
# HOSTS & CSRF
# -------------------------------------------------
_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split() if h.strip()]
# Default to allowing Cloud Run domains if no hosts specified
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]  # Cloud Run handles host validation at ingress

_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split() if o.strip()]
# Add Cloud Run pattern if not set
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "https://*.run.app",
        "https://shoebsiracademy.org",
        "https://www.shoebsiracademy.org",
    ]

# -------------------------------------------------
# DATABASE (BUILD-SAFE + RUNTIME-STRICT)
# -------------------------------------------------
# -------------------------------------------------
# DATABASE (CL explicitly configured)
# -------------------------------------------------
# -------------------------------------------------
# DATABASE (CL explicitly configured)
# -------------------------------------------------
# -------------------------------------------------
# DATABASE (CL explicitly configured)
# -------------------------------------------------
# Explicit Debug for Cloud Run Jobs
print(f"DEBUG: Loading settings. DB_HOST={os.environ.get('DB_HOST')}, DB_USER={os.environ.get('DB_USER')}")

# BUILD PHASE (Collectstatic / Docker Build)
if os.environ.get("DJANGO_BUILD_PHASE"):
    print("DEBUG: Build phase detected. Using dummy SQLite.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    # RUNTIME (Production / Cloud Run)
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")

    if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            f"Missing required database environment variables. "
            f"Found: DB_NAME={bool(DB_NAME)}, DB_USER={bool(DB_USER)}, "
            f"DB_PASSWORD={bool(DB_PASSWORD)}, DB_HOST={bool(DB_HOST)}, DB_PORT={bool(DB_PORT)}"
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "CONN_MAX_AGE": 60,  # Safe for Cloud Run
            "ATOMIC_REQUESTS": True,
        }
    }

# -------------------------------------------------
# STATIC FILES (WHITENOISE)
# -------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# -------------------------------------------------
# MEDIA FILES (GCS – BUILD SAFE)
# -------------------------------------------------
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")

if GS_BUCKET_NAME:
    # Runtime: Google Cloud Storage
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {
                "bucket_name": GS_BUCKET_NAME,
                "querystring_auth": False,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

else:
    # Build-time fallback (NO GCS AVAILABLE)
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    MEDIA_URL = "/media/"

# -------------------------------------------------
# CLOUD RUN / PROXY
# -------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# -------------------------------------------------
# SECURITY
# -------------------------------------------------
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# -------------------------------------------------
# FIREBASE CONFIG
# -------------------------------------------------
_firebase_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
if _firebase_key:
    FIREBASE_SERVICE_ACCOUNT_KEY = _firebase_key

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
