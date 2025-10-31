#!/bin/bash
# Script to set up Ollama with required models

set -e

echo "Waiting for Ollama to be ready..."
sleep 5

echo "Pulling llama2 model..."
docker-compose exec ollama ollama pull llama2

echo "Pulling embedding model (if available)..."
docker-compose exec ollama ollama pull nomic-embed-text || echo "Embedding model not available, will use sentence-transformers"

echo "Listing available models..."
docker-compose exec ollama ollama list

echo "Ollama setup complete!"
