#!/bin/bash
# Railway startup script for MediQuery AI Backend

# Change to backend directory
cd /app/backend

# Set Python path to backend directory so 'app' module can be found
export PYTHONPATH=/app/backend:$PYTHONPATH

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
