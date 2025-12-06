# Django on Google Cloud Run: Complete Deployment Guide

This guide covers the step-by-step process to containerize and deploy your Django application (`coaching_system`) to Google Cloud Run.

## 1. Prerequisites

Before starting, ensure you have:
1.  **Google Cloud Project**: Created with billing enabled.
2.  **Google Cloud SDK (`gcloud`)**: Installed and initialized locally (`gcloud init`).
3.  **APIs Enabled**:
    ```bash
    gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com
    ```

## 2. Project Setup (Files Created)

We have already created the following files in your project root:

### A. `Dockerfile`
Defines the container image. Key features:
-   Uses `python:3.10-slim` for a small footprint.
-   Installs `libpq-dev` for PostgreSQL support.
-   Runs `collectstatic` during the build (using a dummy secret key).
-   Uses `gunicorn` as the production WSGI server.

### B. `.dockerignore`
Excludes unnecessary files (venv, git, local envs) to keep the image small and secure.

### C. `requirements.txt`
Updated to include:
-   `gunicorn`: WSGI server.
-   `psycopg2-binary`: PostgreSQL adapter.
-   `django-storages[google]` & `google-cloud-storage`: For media files on GCS.

### D. `cloudbuild.yaml`
Configuration for Cloud Build CI/CD (explained in Section 7).

## 3. Configuration (`settings.py`)

Ensure your `coaching_system/settings.py` handles production settings correctly.

### Environment Variables
Your settings should read from environment variables:
```python
import os
import dj_database_url

SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_in_production")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# Database
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600
    )
}
```

### CSRF Trusted Origins (Critical for Cloud Run)
Cloud Run sits behind a load balancer, so you must trust the origin:
```python
CSRF_TRUSTED_ORIGINS = ["https://*.run.app"]
# Add your custom domain here later, e.g., "https://www.example.com"
```

### Static & Media Files
-   **Static**: Handled by `whitenoise`.
    ```python
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware', # Add this after SecurityMiddleware
        # ...
    ]
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    ```
-   **Media**: Handled by Google Cloud Storage (GCS).
    ```python
    if not DEBUG:
        DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
        GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
    ```

## 4. GCP Resources Setup

Run these commands in your terminal (PowerShell or Bash):

### 1. Create Artifact Registry Repo
Store your Docker images here.
```bash
gcloud artifacts repositories create my-repo --repository-format=docker --location=us-central1
```

### 2. Create Cloud SQL Instance (PostgreSQL)
```bash
gcloud sql instances create my-db-instance --database-version=POSTGRES_15 --cpu=1 --memory=3840MiB --region=us-central1
```
*Set the root password:*
```bash
gcloud sql users set-password postgres --instance=my-db-instance --password=YOUR_DB_PASSWORD
```
*Create the database:*
```bash
gcloud sql databases create coaching_db --instance=my-db-instance
```

### 3. Create GCS Bucket (Media Files)
```bash
gcloud storage buckets create gs://your-unique-bucket-name --location=us-central1
```
*Make it public (if media files should be public):*
```bash
gcloud storage buckets add-iam-policy-binding gs://your-unique-bucket-name --member=allUsers --role=roles/storage.objectViewer
```

## 5. Build and Deploy

### Option A: Manual Deploy (Fastest for first time)

1.  **Build & Push Image**:
    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/my-repo/django-app
    ```

2.  **Deploy to Cloud Run**:
    Replace placeholders with your actual values.
    ```bash
    gcloud run deploy django-app \
      --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/my-repo/django-app \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars "DEBUG=False" \
      --set-env-vars "SECRET_KEY=your-super-secret-key" \
      --set-env-vars "ALLOWED_HOSTS=*" \
      --set-env-vars "GS_BUCKET_NAME=your-unique-bucket-name" \
      --set-env-vars "DATABASE_URL=postgres://postgres:YOUR_DB_PASSWORD@/coaching_db?host=/cloudsql/YOUR_PROJECT_ID:us-central1:my-db-instance" \
      --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:my-db-instance
    ```

### Option B: CI/CD with Cloud Build
1.  Connect your GitHub repository to Cloud Build.
2.  Create a Trigger pointing to `cloudbuild.yaml`.
3.  Set Substitution variables (`_DATABASE_URL`, `_SECRET_KEY`) in the Trigger settings.

## 6. Post-Deployment Steps

### Run Migrations
You cannot run `manage.py` directly on the running instance easily. Use a "Job" or a temporary container.
```bash
gcloud run jobs create migrate-job \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/my-repo/django-app \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=postgres://postgres:YOUR_DB_PASSWORD@/coaching_db?host=/cloudsql/YOUR_PROJECT_ID:us-central1:my-db-instance" \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:my-db-instance \
  --command python,manage.py,migrate

gcloud run jobs execute migrate-job
```

### Create Superuser
Similar to migrations, run a one-off command:
```bash
gcloud run jobs create create-superuser \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/my-repo/django-app \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=..." \
  --add-cloudsql-instances ... \
  --command python,manage.py,createsuperuser,--noinput,--username,admin,--email,admin@example.com
```
*(Note: You'll need to set the password via environment variable or shell if using a custom script, or just run it locally connecting to the Cloud SQL proxy).*

## 7. Custom Domain & HTTPS
1.  Go to **Cloud Run** console > **Manage Custom Domains**.
2.  Add Mapping > Select Service (`django-app`) > Select Domain.
3.  Update your DNS records (A/AAAA) as shown.
4.  Google automatically provisions a managed SSL certificate.

## 8. Common Errors & Fixes

-   **502 Bad Gateway**: Usually means Gunicorn failed to start. Check logs: `gcloud logging read "resource.type=cloud_run_revision"`.
-   **Static Files 404**: Ensure `whitenoise` is configured and `collectstatic` ran during build.
-   **Database Connection Failed**: Ensure `--add-cloudsql-instances` is set and the Service Account has "Cloud SQL Client" role.
-   **CSRF Failed**: Add the Cloud Run URL (e.g., `https://django-app-xyz.a.run.app`) to `CSRF_TRUSTED_ORIGINS` in `settings.py`.

## 9. Cost Optimization
-   **Cloud Run**: Set "Minimum instances" to 0 (scales to zero when unused).
-   **Cloud SQL**: Stop the instance when not in use (dev) or use Cloud SQL Enterprise Plus for auto-scaling (prod).
