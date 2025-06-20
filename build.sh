#!/usr/bin/env bash
set -o errexit

echo "=== Starting build process ==="

echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Installing Node.js dependencies..."
cd frontend
npm ci --only=production
echo "Building frontend..."
npm run build
cd ..

echo "Setting up static files..."
mkdir -p backend/static
if [ -d "frontend/dist" ]; then
    cp -r frontend/dist/* backend/static/
    echo "Frontend copied successfully"
else
    echo "Warning: frontend/dist not found"
fi

echo "=== Build completed ==="
