#!/bin/bash
# Script to set up Ollama with required models

set -e

echo "Waiting for Ollama to be ready..."
sleep 5

echo "Pulling llama3.2 model..."
docker compose -f docker/docker-compose.yml exec ollama ollama pull llama3.2

echo "Pulling embedding model (if available)..."
docker compose -f docker/docker-compose.yml exec ollama ollama pull nomic-embed-text || echo "Embedding model not available, will use sentence-transformers"

echo "Listing available models..."
docker compose -f docker/docker-compose.yml exec ollama ollama list

echo "Ollama setup complete!"
