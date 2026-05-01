FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=docker

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY data ./data
COPY sql ./sql
RUN pip install --upgrade pip && \
    pip install . && \
    useradd --create-home --shell /usr/sbin/nologin appuser && \
    chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "my_project.cli", "run"]
