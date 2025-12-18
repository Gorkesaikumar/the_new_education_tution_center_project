from .base import *
import os
import dj_database_url

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
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Build-time safe dummy DB (Cloud Run build step)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.dummy"
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
                "default_acl": "public-read",
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
