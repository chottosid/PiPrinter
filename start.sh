#!/bin/bash

# PiPrinter Startup Script

echo "Starting PiPrinter..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start the application
echo "Starting application at http://localhost:8000"
python -m app.main
