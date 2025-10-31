#!/bin/bash
# Script to setup Python virtual environment for local development

set -e

echo "==================================="
echo "FastAPI ML - Virtual Environment Setup"
echo "==================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python version: $PYTHON_VERSION"

# Check if Python 3.11+ is available
if ! command -v python3.11 &> /dev/null; then
    echo "Warning: Python 3.11 not found, using default python3"
    PYTHON_CMD="python3"
else
    echo "Using Python 3.11"
    PYTHON_CMD="python3.11"
fi

# Remove old venv if exists
if [ -d "venv" ]; then
    echo ""
    read -p "Virtual environment already exists. Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
    else
        echo "Keeping existing virtual environment"
        exit 0
    fi
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies if available
if [ -f "requirements-dev.txt" ]; then
    echo ""
    read -p "Install development dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Summary
echo ""
echo "==================================="
echo "Setup completed successfully!"
echo "==================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start PostgreSQL and Ollama services"
echo "3. Initialize database: python -m app.db.init_db"
echo "4. Run the application: uvicorn app.main:app --reload"
echo ""
echo "Happy coding!"
