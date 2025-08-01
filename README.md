# FlatFund Backend Development

## � Documentation

**🔗 [Complete API Documentation](./API_DOCUMENTATION.md)** - Comprehensive guide to all endpoints, requests, responses, and authentication flows.

## �🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your local settings

# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Docker
docker-compose up --build
```

### Testing
```bash
# Test API
curl http://localhost:8000/api/v1/apartments/

# Admin UI
open http://localhost:8000/static/admin.html
```

## 📦 Deployment Workflow

### 1. Make Changes Locally
```bash
# Edit files in your local environment
# Test changes locally first
```

### 2. Commit Changes
```bash
git add .
git commit -m "Description of changes"
```

### 3. Deploy to Server
```bash
# Package for deployment
./package-for-deployment.sh

# Upload to server
scp /tmp/flatfund-backend-*.tar.gz ubuntu@your-server:/tmp/

# Deploy on server
ssh ubuntu@your-server
cd /tmp && tar -xzf flatfund-backend-*.tar.gz
sudo cp -r flatfund-backend-*/* /opt/flatfund/
cd /opt/flatfund && sudo docker-compose up --build -d
```

## 🌐 Production URLs

- **API**: https://flatfund.duckdns.org/api/v1/apartments/
- **Admin**: https://flatfund.duckdns.org/static/admin.html  
- **Docs**: https://flatfund.duckdns.org/docs

## 🔧 Environment Variables

Copy `.env.example` to `.env` and update:

```bash
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=flatfund.duckdns.org,localhost
CORS_ORIGINS=https://flatfund.duckdns.org
USE_LOCAL_DB=true
DATABASE_URL=sqlite:///./flatfund.db
```

## 📱 API Schema

### Create Apartment
```json
POST /api/v1/apartments/
{
  "apartment_name": "string",
  "apartment_address": "string", 
  "admin_email": "email@example.com"
}
```

### Response
```json
{
  "id": "uuid",
  "apartment_id": "SHORT_ID",
  "apartment_name": "string",
  "apartment_address": "string",
  "admin_email": "string"
}
```
