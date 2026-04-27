FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    APP_ENV=dev

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY data ./data
COPY sql ./sql
RUN pip install --upgrade pip && pip install .
CMD ["python", "-m", "my_project.cli", "run", "--env", "dev"]
