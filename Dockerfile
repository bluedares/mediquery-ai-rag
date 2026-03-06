# MediQuery AI Backend - Railway Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY backend/requirements-minimal.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create directory for ChromaDB persistence
RUN mkdir -p /app/chroma_data

# Expose port
EXPOSE 8000

# Start command - Railway will inject PORT env var
CMD python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
