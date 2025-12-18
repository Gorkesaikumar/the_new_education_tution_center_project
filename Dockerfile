# =========================
# BUILDER STAGE
# =========================
FROM python:3.10-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies ONLY here
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and build wheels
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


# =========================
# RUNTIME STAGE
# =========================
FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=coaching_system.settings.production
ENV PYTHONPATH=/app

WORKDIR /app

# Install ONLY runtime system deps
RUN apt-get update && apt-get install -y \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copy project code
COPY . .

# Collect static safely (NO DB access)
RUN SECRET_KEY=dummy_build_key \
    DJANGO_ALLOW_NO_DB=1 \
    python manage.py collectstatic --noinput

# Create non-root user (Cloud Run best practice)
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# IMPORTANT: enable full logging for Cloud Run
CMD ["gunicorn","--bind","0.0.0.0:8080","--workers","2","--threads","8","--timeout","120","--log-level","debug","--access-logfile","-","--error-logfile","-","coaching_system.wsgi:application"]
