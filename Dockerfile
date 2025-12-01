FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off 
  

WORKDIR /app

# system deps needed for psycopg2 and building some packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# copy dependencies first (leverage layer caching)
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

# copy source
COPY src /app/src

# non-root user (optional)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT} --app-dir src"]