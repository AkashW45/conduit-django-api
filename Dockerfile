# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# System deps that many Python wheels need
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so docker layer caching is useful
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

EXPOSE 8000

# Tini-style PID 1 isn't strictly needed for Lambda/ECS Fargate but doesn't hurt
CMD ["sh", "-c", "gunicorn conduit.wsgi:application --bind 0.0.0.0:8000"]
