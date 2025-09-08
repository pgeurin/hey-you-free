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

# Start the application
python -m src.api.server
