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
    
    # Stop and remove all containers and images
    cd $DEPLOY_PATH
    echo "🛑 Stopping and removing existing containers..."
    sudo docker-compose down --volumes --remove-orphans || true
    
    # Remove all flatfund related images to force rebuild
    echo "🗑️  Removing cached Docker images..."
    sudo docker images | grep flatfund | awk '{print \$3}' | sudo xargs docker rmi -f 2>/dev/null || true
    sudo docker system prune -f || true
    
    # Deploy new version - ensure complete replacement
    echo "📁 Deploying new files..."
    sudo rm -rf $DEPLOY_PATH/static/* || true
    sudo rm -rf $DEPLOY_PATH/app/* || true
    sudo cp -r /tmp/$PACKAGE_NAME/* $DEPLOY_PATH/
    sudo chown -R ubuntu:ubuntu $DEPLOY_PATH
    
    # Force complete rebuild without any cache
    cd $DEPLOY_PATH
    echo "🏗️  Building fresh Docker images (no cache)..."
    sudo docker-compose build --no-cache --pull --force-rm
    
    # Start services
    echo "🚀 Starting services..."
    sudo docker-compose up -d
    
    # Check service status
    echo "⏳ Waiting for services to start..."
    sleep 15
    sudo docker-compose ps
    
    # Verify static files are updated
    echo "📋 Verifying deployment..."
    if grep -q "Quattrocento" $DEPLOY_PATH/static/admin.html; then
        echo "✅ Static files updated successfully"
    else
        echo "⚠️  Warning: Static files may not be updated properly"
    fi
    
    echo "✅ Deployment completed!"
    echo "🌐 API: https://flatfund.duckdns.org/api/v1/apartments/"
    echo "🏠 Admin: https://flatfund.duckdns.org/static/admin.html"
EOF

echo ""
echo "🎉 Deployment successful!"
echo "Your application is now running at: https://flatfund.duckdns.org"
