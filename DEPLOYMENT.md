# heyyoufree - GCP Deployment Guide

This guide covers deploying the heyyoufree AI-powered meeting scheduler to Google Cloud Platform.

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed (for local testing)
4. **Google Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 1. Setup Google Cloud Project

```bash
# Create a new project (or use existing)
gcloud projects create heyyoufree-$(date +%s) --name="heyyoufree"

# Set the project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Configure Environment

```bash
# Copy the production environment template
cp env.production.template .env.production

# Edit the file with your actual values
nano .env.production
```

Required environment variables:
- `GOOGLE_API_KEY`: Your Gemini AI API key
- `SECRET_KEY`: A secure random string for production
- `ALLOWED_ORIGINS`: Your production domain(s)

### 3. Deploy to Cloud Run

```bash
# Run the deployment script
./deploy.sh
```

Or deploy manually:

```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml
```

## 🐳 Local Docker Testing

Test the container locally before deploying:

```bash
# Run the Docker test script
./test-docker.sh
```

Or manually:

```bash
# Build the image
docker build -t heyyoufree:latest .

# Run the container
docker run -d -p 8000:8000 \
  -e GOOGLE_API_KEY="your_api_key" \
  -e DEBUG=false \
  heyyoufree:latest

# Test the endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
curl http://localhost:8000/scheduler
```

## 📊 Monitoring & Logs

### View Logs
```bash
# Cloud Run logs
gcloud run services logs read heyyoufree --region=us-central1

# Real-time logs
gcloud run services logs tail heyyoufree --region=us-central1
```

### Health Monitoring
- **Health Check**: `https://your-service-url/health`
- **Landing Page**: `https://your-service-url/`
- **Scheduler**: `https://your-service-url/scheduler`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini AI API key | Required |
| `SERVER_HOST` | Server host | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format (json/text) | `json` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit | `60` |
| `SECRET_KEY` | Secret key for security | Required |
| `ALLOWED_ORIGINS` | CORS origins | Required |

### Update Environment Variables

```bash
gcloud run services update heyyoufree \
  --region=us-central1 \
  --set-env-vars="KEY=VALUE"
```

## 🏗️ Architecture

### Production Features

- ✅ **Rate Limiting**: 10/min API, 20/min chat, 5/min OAuth
- ✅ **Structured Logging**: JSON format for production
- ✅ **Health Checks**: System metrics and service status
- ✅ **Error Handling**: Global exception handler with request tracking
- ✅ **Security**: CORS configuration, secret keys
- ✅ **Monitoring**: Request logging with timing and status codes

### GCP Services Used

- **Cloud Run**: Serverless container platform
- **Cloud Build**: CI/CD pipeline
- **Container Registry**: Docker image storage
- **Cloud Logging**: Centralized logging
- **Cloud Monitoring**: Health and performance monitoring

## 🔒 Security

### Production Security Checklist

- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_ORIGINS` for your domain
- [ ] Enable HTTPS only
- [ ] Set up proper IAM roles
- [ ] Use Cloud SQL for production database
- [ ] Enable Cloud Security Command Center
- [ ] Set up monitoring alerts

### IAM Roles

Required roles for deployment:
- `Cloud Run Admin`
- `Cloud Build Editor`
- `Storage Admin` (for Container Registry)

## 📈 Scaling

### Auto-scaling Configuration

The application is configured with:
- **Min instances**: 1
- **Max instances**: 10
- **CPU utilization**: 60%
- **Memory**: 1GB
- **CPU**: 1 vCPU

### Performance Optimization

- **Container startup**: ~10-15 seconds
- **Cold start**: Optimized with health checks
- **Memory usage**: ~200-400MB typical
- **Response time**: <500ms for most endpoints

## 🚨 Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile and dependencies
2. **Service won't start**: Check environment variables
3. **Health check fails**: Verify port configuration
4. **Rate limiting**: Adjust `RATE_LIMIT_PER_MINUTE`

### Debug Commands

```bash
# Check service status
gcloud run services describe heyyoufree --region=us-central1

# View recent logs
gcloud run services logs read heyyoufree --region=us-central1 --limit=50

# Test health endpoint
curl -v https://your-service-url/health
```

## 🔄 CI/CD Pipeline

The `cloudbuild.yaml` file sets up automatic deployment:

1. **Build**: Creates Docker image
2. **Push**: Uploads to Container Registry
3. **Deploy**: Updates Cloud Run service

### Manual Deployment

```bash
# Build and push
gcloud builds submit --config cloudbuild.yaml

# Or use the deploy script
./deploy.sh
```

## 📞 Support

For issues or questions:
1. Check the logs: `gcloud run services logs read heyyoufree --region=us-central1`
2. Verify environment variables
3. Test locally with Docker first
4. Check GCP service status

## 🎯 Next Steps

After successful deployment:
1. Set up custom domain
2. Configure Cloud SQL for production database
3. Set up monitoring alerts
4. Configure backup strategies
5. Set up staging environment
