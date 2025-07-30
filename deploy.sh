#!/bin/bash

# Deployment script for FlatFund Backend
# Usage: ./deploy.sh

set -e

echo "🚀 FlatFund Deployment Script"
echo "=============================="

# Configuration
SERVER_IP="3.110.126.142"
SERVER_USER="ubuntu"
KEY_FILE="flatfund-backend.pem"
DEPLOY_PATH="/opt/flatfund"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file $KEY_FILE not found!"
    echo "Please ensure your SSH key is in the current directory"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
./package-for-deployment.sh

# Get the latest package
PACKAGE_FILE=$(ls -t /tmp/flatfund-backend-*.tar.gz | head -1)
PACKAGE_NAME=$(basename "$PACKAGE_FILE" .tar.gz)

echo "📤 Uploading package to server..."
scp -i "$KEY_FILE" "$PACKAGE_FILE" "$SERVER_USER@$SERVER_IP:/tmp/"

echo "🔧 Deploying on server..."
ssh -i "$KEY_FILE" "$SERVER_USER@$SERVER_IP" << EOF
    # Extract package
    cd /tmp
    tar -xzf $PACKAGE_NAME.tar.gz
    
    # Backup current deployment
    sudo cp -r $DEPLOY_PATH $DEPLOY_PATH.backup.\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
    
    # Deploy new version
    sudo cp -r $PACKAGE_NAME/* $DEPLOY_PATH/
    
    # Restart services
    cd $DEPLOY_PATH
    sudo docker-compose down
    sudo docker-compose up --build -d
    
    # Check service status
    sleep 5
    sudo docker-compose ps
    
    echo "✅ Deployment completed!"
    echo "🌐 API: https://flatfund.duckdns.org/api/v1/apartments/"
    echo "🏠 Admin: https://flatfund.duckdns.org/static/admin.html"
EOF

echo ""
echo "🎉 Deployment successful!"
echo "Your application is now running at: https://flatfund.duckdns.org"
