#!/bin/bash
# Run comprehensive test suite with coverage

set -e

echo "=== Running Test Suite ==="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create required directories
mkdir -p data logs cache htmlcov

# Run pytest with coverage
echo "Running tests with coverage..."
pytest tests/ -v \
    --cov=src \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    --tb=short

echo ""
echo "=== Test Results ==="
echo ""

# Display coverage summary
echo "Coverage report generated in htmlcov/index.html"

# Check if coverage meets threshold
coverage report --fail-under=85 || {
    echo ""
    echo "WARNING: Code coverage is below 85%"
    exit 1
}

echo ""
echo "=== All Tests Passed ==="
