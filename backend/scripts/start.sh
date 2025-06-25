#!/bin/bash

# Exit on any error
set -e

echo "Starting DynamicContractOps Backend..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload