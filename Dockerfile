# Single-stage build for MediQuery AI Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements-minimal.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements-minimal.txt

# Copy application code
COPY backend/ /app/backend/

# Set Python path
ENV PYTHONPATH=/app

# Create directory for ChromaDB persistence
RUN mkdir -p /app/chroma_data

# Expose port (Railway will override this with dynamic PORT)
EXPOSE 8000

# Run the application
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
