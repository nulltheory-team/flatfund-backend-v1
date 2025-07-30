#!/bin/bash

# Package application for deployment
# This script creates a deployment-ready package

set -e

echo "📦 Packaging FlatFund Backend for Deployment"
echo "============================================"

# Create deployment package
PACKAGE_NAME="flatfund-backend-$(date +%Y%m%d-%H%M%S)"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"

echo "📁 Creating package directory: $PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy application files
echo "📋 Copying application files..."
cp -r app/ "$PACKAGE_DIR/"
cp -r static/ "$PACKAGE_DIR/"
cp Dockerfile "$PACKAGE_DIR/"
cp docker-compose.yml "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp .dockerignore "$PACKAGE_DIR/"
cp .env.example "$PACKAGE_DIR/"
cp deploy-aws.sh "$PACKAGE_DIR/"

# Copy additional files if they exist
[ -f "README.md" ] && cp README.md "$PACKAGE_DIR/"
[ -f "init_rds.py" ] && cp init_rds.py "$PACKAGE_DIR/"

# Create deployment instructions
cat > "$PACKAGE_DIR/DEPLOYMENT.md" << 'EOF'
# FlatFund Backend Deployment Guide

## 🚀 Quick Deployment to AWS EC2

### Prerequisites
- AWS EC2 instance (Ubuntu 20.04+ recommended)
- Security Group allowing ports 22, 80, 443, 8000
- SSH access to the instance

### Step 1: Upload Files
```bash
# Upload the package to your EC2 instance
scp -r flatfund-backend-* ubuntu@your-ec2-ip:/home/ubuntu/
```

### Step 2: Run Deployment Script
```bash
# SSH into your EC2 instance
ssh ubuntu@your-ec2-ip

# Navigate to the uploaded directory
cd flatfund-backend-*

# Make script executable and run
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### Step 3: Deploy Application
```bash
# Copy files to deployment directory
sudo cp -r * /opt/flatfund/

# Start the application
cd /opt/flatfund
sudo systemctl start flatfund

# Check status
sudo systemctl status flatfund
```

### Step 4: Test Your Deployment
- API: http://your-ec2-ip/api/v1/apartments/
- Docs: http://your-ec2-ip/docs
- Admin UI: http://your-ec2-ip/static/admin.html

### Environment Configuration
Edit `/opt/flatfund/.env` to configure:
- Database connection
- CORS settings
- Security keys

### Logs and Monitoring
```bash
# View application logs
cd /opt/flatfund && sudo docker-compose logs -f

# Check service status
sudo systemctl status flatfund
sudo systemctl status nginx
sudo systemctl status docker
```

### HTTPS Setup (Optional)
```bash
# Install SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com
```

## 🔧 Local Docker Testing

Before deploying, test locally:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Test the API
curl http://localhost:8000/api/v1/apartments/
```

## 📊 Troubleshooting

### Application not starting
```bash
sudo docker-compose logs
sudo systemctl status flatfund
```

### Database connection issues
```bash
# Check RDS connectivity
python3 init_rds.py
```

### Port issues
```bash
# Check what's using port 8000
sudo netstat -tulpn | grep 8000
```
EOF

# Create a simple deployment checklist
cat > "$PACKAGE_DIR/CHECKLIST.md" << 'EOF'
# Deployment Checklist

## 🔐 Security Configuration
- [ ] Change default passwords in .env
- [ ] Update SECRET_KEY in .env
- [ ] Configure proper CORS origins
- [ ] Set up SSL certificate (HTTPS)
- [ ] Review firewall rules

## 🌐 AWS Configuration
- [ ] EC2 instance launched (t2.micro for free tier)
- [ ] Security group allows ports 22, 80, 443
- [ ] SSH key pair configured
- [ ] Elastic IP assigned (optional)

## 📊 Database Configuration
- [ ] RDS instance accessible from EC2
- [ ] Database credentials configured
- [ ] Security group allows database access

## 🚀 Application Deployment
- [ ] Files uploaded to EC2
- [ ] Deployment script executed
- [ ] Docker and services running
- [ ] Application responds to requests
- [ ] Admin UI accessible

## 📈 Post-Deployment
- [ ] Monitor application logs
- [ ] Set up automated backups
- [ ] Configure monitoring/alerts
- [ ] Document access URLs
- [ ] Test all API endpoints
EOF

# Create archive
echo "🗜️ Creating deployment archive..."
cd /tmp
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

echo ""
echo "✅ Package created successfully!"
echo "================================"
echo ""
echo "📦 Package location: /tmp/$PACKAGE_NAME.tar.gz"
echo "📁 Package directory: $PACKAGE_DIR"
echo ""
echo "📋 Next steps:"
echo "1. Copy /tmp/$PACKAGE_NAME.tar.gz to your local machine"
echo "2. Upload it to your AWS EC2 instance"
echo "3. Extract and run the deployment script"
echo ""
echo "💡 Quick upload command:"
echo "   scp /tmp/$PACKAGE_NAME.tar.gz ubuntu@your-ec2-ip:/home/ubuntu/"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"
