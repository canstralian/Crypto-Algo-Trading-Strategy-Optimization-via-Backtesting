#!/bin/bash
# Setup script for the crypto trading platform

set -e

echo "=== Crypto Trading Platform Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing development dependencies..."
pip install -r requirements-dev.txt

# Create required directories
echo "Creating required directories..."
mkdir -p data logs cache config

# Copy configuration files if they don't exist
if [ ! -f "config/config.yaml" ]; then
    echo "Copying configuration files..."
    cp config/config.example.yaml config/config.yaml
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v --cov=src"
echo ""
echo "To start the API server:"
echo "  uvicorn src.api.main:app --reload"
echo ""
