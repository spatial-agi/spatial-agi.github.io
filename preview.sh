#!/bin/bash

# Quick local server for previewing the website
# Usage: ./preview.sh

PORT=8000

echo "🚀 Starting local preview server..."
echo "📍 URL: http://localhost:$PORT"
echo "⌨️  Press Ctrl+C to stop"
echo ""

# Try Python 3 first, then Python 2, then Node.js
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer $PORT
elif command -v npx &> /dev/null; then
    npx http-server -p $PORT
else
    echo "❌ Error: No suitable HTTP server found"
    echo "Please install Python 3 or Node.js to run the preview server"
    exit 1
fi
