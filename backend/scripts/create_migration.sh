#!/bin/bash

# Create a new Alembic migration
if [ -z "$1" ]; then
    echo "Usage: $0 <migration_message>"
    exit 1
fi

echo "Creating new migration: $1"
alembic revision --autogenerate -m "$1"