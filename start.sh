#!/bin/bash

# Railway startup script
echo "Starting heyyoufree application... (v2.0)"

# Check if required environment variables are set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "WARNING: GOOGLE_API_KEY not set. AI features may not work."
fi

# Set default port if not provided
export PORT=${PORT:-8000}

echo "Starting server on port $PORT..."
echo "Environment variables:"
echo "PORT=$PORT"
echo "GOOGLE_API_KEY=${GOOGLE_API_KEY:0:10}..." 
echo "All env vars:"
env | grep -E "(PORT|GOOGLE|RAILWAY)" || echo "No relevant env vars found"

# Start the application
python -m src.api.server
