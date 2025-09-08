#!/bin/bash

# heyyoufree Docker Test Script
# This script builds and tests the Docker container locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 heyyoufree Docker Test Script${NC}"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker build -t heyyoufree:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Run the container
echo -e "${BLUE}🚀 Starting container...${NC}"
docker run -d \
    --name heyyoufree-test \
    -p 8000:8000 \
    -e GOOGLE_API_KEY="${GOOGLE_API_KEY:-your_api_key_here}" \
    -e DEBUG=false \
    -e LOG_LEVEL=INFO \
    -e LOG_FORMAT=json \
    heyyoufree:latest

# Wait for container to start
echo -e "${YELLOW}⏳ Waiting for container to start...${NC}"
sleep 10

# Test health endpoint
echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    docker logs heyyoufree-test
    docker stop heyyoufree-test
    docker rm heyyoufree-test
    exit 1
fi

# Test landing page
echo -e "${BLUE}🏠 Testing landing page...${NC}"
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Landing page accessible${NC}"
else
    echo -e "${RED}❌ Landing page failed${NC}"
fi

# Test scheduler page
echo -e "${BLUE}📅 Testing scheduler page...${NC}"
if curl -f http://localhost:8000/scheduler > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Scheduler page accessible${NC}"
else
    echo -e "${RED}❌ Scheduler page failed${NC}"
fi

# Show container logs
echo -e "${BLUE}📋 Container logs:${NC}"
docker logs heyyoufree-test --tail 20

# Cleanup
echo -e "${BLUE}🧹 Cleaning up...${NC}"
docker stop heyyoufree-test
docker rm heyyoufree-test

echo -e "${GREEN}✅ Docker test completed successfully!${NC}"
echo -e "${BLUE}🌐 The application is ready for GCP deployment${NC}"
