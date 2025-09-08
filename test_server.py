#!/usr/bin/env python3
"""
Simple test server to debug Railway deployment issues
"""
import os
import sys
from fastapi import FastAPI

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "Test server is working!", "port": os.environ.get("PORT", "not set")}

@app.get("/health")
async def health():
    return {"status": "healthy", "port": os.environ.get("PORT", "not set")}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting test server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
