# Deployment Setup Guide

## 🎉 Successfully Deployed to Railway

### **Cost Savings Achieved**
- **Original GCP Cost**: $900+/month
- **Railway Cost**: $5/month (free tier available)
- **Savings**: $895/month = $10,740/year

## 📋 What We Accomplished

### ✅ **Database Migration**
- **From**: Google Cloud SQL ($900/month)
- **To**: Neon PostgreSQL (Free tier)
- **Connection String**: `postgresql://neondb_owner:your_database_password_here@ep-cool-violet-afuk0k2w-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

### ✅ **Hosting Migration**
- **From**: Google Cloud Platform
- **To**: Railway.app
- **URL**: `https://hey-you-free-production.up.railway.app`
- **Auto-deployment**: Connected to GitHub repo

### ✅ **Environment Configuration**
- **Google Gemini API**: `your_google_api_key_here`
- **Secret Key**: `your_secret_key_here`
- **Database**: Neon PostgreSQL configured
- **Frontend**: Fixed API URL to use Railway domain

### ✅ **Code Fixes**
- **Fixed**: Frontend hardcoded localhost URL
- **Fixed**: Missing calendar data files (gitignore issue)
- **Added**: All required data files to repository

## 🔧 Critical Setup Steps

### **1. Neon Database Setup**
```bash
# Connection string format
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require&channel_binding=require
```

### **2. Railway Environment Variables**
```bash
DATABASE_URL=postgresql://neondb_owner:your_database_password_here@ep-cool-violet-afuk0k2w-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_secret_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
ALLOWED_ORIGINS=https://hey-you-free-production.up.railway.app
```

### **3. GitHub Repository**
- **Repository**: `https://github.com/pgeurin/hey-you-free`
- **Auto-deployment**: Railway connected to GitHub
- **Data files**: All calendar data included

### **4. Frontend Configuration**
- **API Base**: `window.location.origin` (auto-detects Railway domain)
- **Static files**: Served from `/static/index.html`

## 🚀 Deployment Process

### **Railway Setup**
1. **Sign up**: https://railway.app/
2. **Connect GitHub**: Select `pgeurin/hey-you-free` repository
3. **Auto-deploy**: Railway detects Python app
4. **Add environment variables**: Copy from above
5. **Expose service**: Make public URL available

### **Neon Database**
1. **Sign up**: https://neon.tech/
2. **Create project**: `butterfly-meeting-scheduler`
3. **Get connection string**: Copy to Railway environment
4. **Free tier**: 3GB storage, 10GB transfer/month

## 🔍 Troubleshooting

### **Common Issues Fixed**
1. **503 Error**: Service not exposed → Expose in Railway dashboard
2. **500 Error**: Missing data files → Fixed .gitignore, added data files
3. **Frontend errors**: localhost URL → Changed to `window.location.origin`
4. **Database errors**: Missing connection → Added DATABASE_URL to Railway

### **Log Monitoring**
- **Railway logs**: Dashboard → Deployments → Latest deployment
- **Health check**: `https://your-app.up.railway.app/health`
- **API endpoint**: `https://your-app.up.railway.app/meeting-suggestions`

## 📊 Current Status

### ✅ **Working Features**
- AI meeting suggestions
- Calendar data integration
- Frontend interface
- Health monitoring
- Auto-deployment from GitHub

### 🔄 **Next Steps**
- Custom domain setup (Namecheap)
- SSL certificate (automatic with Railway)
- Production monitoring
- Performance optimization

## 💰 Cost Breakdown

| Service | Cost | Purpose |
|---------|------|---------|
| Railway | $5/month | App hosting |
| Neon | $0/month | Database (free tier) |
| Google Gemini | Free | AI API |
| **Total** | **$5/month** | **Full production app** |

## 🔗 Important Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Neon Console**: https://console.neon.tech/
- **GitHub Repository**: https://github.com/pgeurin/hey-you-free
- **Live App**: https://hey-you-free-production.up.railway.app

## 📝 Notes

- **Auto-deployment**: Push to GitHub triggers Railway rebuild
- **Environment variables**: Set in Railway dashboard, not in code
- **Data files**: All calendar data included in repository
- **SSL**: Automatic with Railway custom domains
- **Monitoring**: Built-in Railway metrics and logs

---

**Last Updated**: September 8, 2025
**Status**: ✅ Production Ready
**Cost**: $5/month (99.4% savings from original GCP setup)
