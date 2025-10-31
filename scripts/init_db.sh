#!/bin/bash
# Script to initialize the database

set -e

echo "Waiting for PostgreSQL to be ready..."
sleep 5

echo "Initializing database and creating tables..."
docker-compose exec api-dev python -m app.db.init_db

echo "Database initialization complete!"
