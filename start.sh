#!/bin/bash

echo "Starting Content Service..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Optionally seed the database
# Set AUTO_SEED=true in .env to enable automatic seeding
echo "Database seeding will run if AUTO_SEED=true in .env"

# Start the FastAPI application
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
