FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.7.1

COPY services/aggregation-service/pyproject.toml services/aggregation-service/poetry.lock* ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

COPY shared /app/shared
COPY services/aggregation-service/ .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH="/app/shared:${PYTHONPATH}"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

