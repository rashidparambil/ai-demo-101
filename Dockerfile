# ...existing code...
FROM python:3.11-slim

# Define build args with defaults
ARG APP_MODULE=src.api.mcp_server_1:app # <--- ADJUSTED APP_MODULE
ARG PORT=8080

# Export to ENV so runtime can use them
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    APP_MODULE=${APP_MODULE} \
    PORT=${PORT}

WORKDIR /app # <--- ADJUSTED WORKDIR (Set to the root of the app)

# system deps needed for psycopg2 and building some packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# copy dependencies first (leverage layer caching)
COPY requirements.txt . # <--- ADJUSTED: Copy to /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt # <--- ADJUSTED: Install from /app/requirements.txt

# copy source
COPY src ./src # <--- ADJUSTED: Copies src folder to /app/src

# non-root user (optional)
# This command is correct for setting user and ownership
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Informational; Cloud Run sets PORT env at runtime (default 8080)
EXPOSE 8080

# Use shell so runtime env vars (APP_MODULE, PORT) are respected by uvicorn
# Uvicorn will import 'src.api.mcp_server_1:app' which finds src/api/mcp_server_1.py
CMD ["sh", "-c", "uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT}"]