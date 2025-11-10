FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    PROJECT_NAME=Tenguin

ARG APP_HOME=/app/backend
ARG APP_USER=appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${APP_HOME} \
    && groupadd -r ${APP_USER} && useradd -r -g ${APP_USER} ${APP_USER} \
    && chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

WORKDIR ${APP_HOME}

COPY requirements.txt ../requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r ../requirements.txt

COPY . .

RUN chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

USER ${APP_USER}

CMD ["sh", "-c", "gunicorn ${PROJECT_NAME}.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
