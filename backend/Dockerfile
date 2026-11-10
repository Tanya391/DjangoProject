# Lightweight production image ~150-200MB

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt \
    && find /usr/local/lib/python3.11 -name "*.pyc" -delete 2>/dev/null || true \
    && find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

COPY . .

# collectstatic — use simple storage to avoid manifest hashing issues at build time
RUN SECRET_KEY=build-time-placeholder-key-for-collectstatic-only-not-used-in-prod \
    DEBUG=false \
    DJANGO_SETTINGS_MODULE=config.settings \
    STATICFILES_STORAGE=django.contrib.staticfiles.storage.StaticFilesStorage \
    python manage.py collectstatic --noinput

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120"]

EXPOSE 8000
