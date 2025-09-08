#!/bin/bash

# heyyoufree GCP Deployment Script
# This script deploys the application to Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 heyyoufree GCP Deployment Script${NC}"
echo "=================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No project ID set. Please run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"

# Check if required APIs are enabled
echo -e "${BLUE}📋 Checking required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy
echo -e "${BLUE}🔨 Building and deploying to Cloud Run...${NC}"
gcloud builds submit --config cloudbuild.yaml

# Get the service URL
SERVICE_URL=$(gcloud run services describe heyyoufree --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
    echo -e "${GREEN}🏥 Health check: $SERVICE_URL/health${NC}"
    echo -e "${GREEN}🏠 Landing page: $SERVICE_URL/${NC}"
    echo -e "${GREEN}📅 Scheduler: $SERVICE_URL/scheduler${NC}"
else
    echo -e "${RED}❌ Deployment failed or service not found${NC}"
    exit 1
fi

echo -e "${BLUE}📊 To view logs, run:${NC}"
echo "gcloud run services logs read heyyoufree --region=us-central1"

echo -e "${BLUE}🔧 To update environment variables, run:${NC}"
echo "gcloud run services update heyyoufree --region=us-central1 --set-env-vars KEY=VALUE"
