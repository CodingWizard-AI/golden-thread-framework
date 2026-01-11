#!/bin/bash
# Script to install dependencies and run tests with coverage

set -e

echo "=== Golden Thread Framework - Test Runner ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install package with dev dependencies
echo "Installing package with dev dependencies..."
pip install -q -e ".[dev]"

# Run tests with coverage
echo ""
echo "Running tests with coverage..."
python -m pytest tests/ \
    --cov=golden_thread \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=json \
    -v

# Display coverage summary
echo ""
echo "=== Coverage Summary ==="
python -m coverage report --skip-empty

# Check coverage threshold
echo ""
echo "=== Coverage Threshold Check ==="
python -m coverage report --skip-empty | grep "TOTAL" | awk '{
    if ($4+0 >= 75) {
        print "✅ Coverage: " $4 " - PASS (threshold: 75%)"
        exit 0
    } else {
        print "❌ Coverage: " $4 " - FAIL (threshold: 75%)"
        exit 1
    }
}'

# Deactivate virtual environment
deactivate

echo ""
echo "HTML coverage report: htmlcov/index.html"
echo "JSON coverage report: coverage.json"
