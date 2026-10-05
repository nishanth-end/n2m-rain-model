FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including OpenMP runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY data/ ./data/
COPY model/ ./model/
COPY backend/ ./backend/
COPY docs/ ./docs/

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}"]
