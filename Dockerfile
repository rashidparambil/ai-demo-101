# ...existing code...
FROM python:3.11-slim

# Define build args with defaults
ARG APP_MODULE=api.mcp_server_1:app
ARG PORT=8080

# Export to ENV so runtime can use them
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    APP_MODULE=${APP_MODULE} \
    PORT=${PORT} \
    PYTHONPATH=/app/src:$PYTHONPATH

WORKDIR /app/src

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

# Informational; Cloud Run sets PORT env at runtime (default 8080)
EXPOSE 8080

# Use shell so runtime env vars (APP_MODULE, PORT) are respected by uvicorn
CMD ["sh", "-c", "uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT}"]
# ...existing code...