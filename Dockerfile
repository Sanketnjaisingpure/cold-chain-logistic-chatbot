FROM python:3.12-slim

WORKDIR /app

COPY req-ingestion.txt .

RUN pip install --no-cache-dir -r req-ingestion.txt

CMD ["python", "scripts/ingest_legacy_data.py"]