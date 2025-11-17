#!/bin/bash

# Script để chạy VNStock API

echo "Starting VNStock API..."
echo "========================================"

# Kích hoạt virtual environment nếu có
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Chạy server
echo "Running server on http://0.0.0.0:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "========================================"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
