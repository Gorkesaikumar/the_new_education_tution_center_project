FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=coaching_system.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
# libpq-dev is needed for psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run collectstatic during build (requires dummy env vars if settings rely on them)
# We set a dummy SECRET_KEY to allow collectstatic to run without the real one
RUN SECRET_KEY=dummy_build_key python manage.py collectstatic --noinput

# Expose the port Cloud Run expects
EXPOSE 8080

# Start Gunicorn
# Replace 'coaching_system.wsgi:application' with your project's WSGI app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "8", "--timeout", "120", "coaching_system.wsgi:application"]
