FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway uses PORT env var
ENV PORT=8000

# Use $PORT for Railway compatibility
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
