FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including OpenMP runtime for XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and ML handover assets
COPY backend/ ./backend/
COPY handover_member3/ ./handover_member3/

ENV PORT=8000
ENV MODE=historical_replay
EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
