#!/bin/bash

# Deployment script for FlatFund Backend
# Usage: ./deploy.sh

set -e

echo "🚀 FlatFund Deployment Script"
echo "=============================="

# Configuration
SERVER_IP="3.111.80.201"
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
    
    # Verify correct file structure
    echo "📋 Verifying deployment structure..."
    if [ -d "$DEPLOY_PATH/app" ] && [ -d "$DEPLOY_PATH/static" ]; then
        echo "✅ Correct structure: app/ and static/ directories exist"
    else
        echo "❌ WARNING: Incorrect structure detected! Fixing..."
        # Fix structure if needed
        sudo mkdir -p $DEPLOY_PATH/app $DEPLOY_PATH/static
        
        # Move Python files to app/ if they're in root
        sudo mv $DEPLOY_PATH/main.py $DEPLOY_PATH/app/ 2>/dev/null || true
        sudo mv $DEPLOY_PATH/models.py $DEPLOY_PATH/app/ 2>/dev/null || true  
        sudo mv $DEPLOY_PATH/crud.py $DEPLOY_PATH/app/ 2>/dev/null || true
        sudo mv $DEPLOY_PATH/database.py $DEPLOY_PATH/app/ 2>/dev/null || true
        sudo mv $DEPLOY_PATH/schemas.py $DEPLOY_PATH/app/ 2>/dev/null || true
        sudo mv $DEPLOY_PATH/routers $DEPLOY_PATH/app/ 2>/dev/null || true
        sudo touch $DEPLOY_PATH/app/__init__.py
        
        # Move static files to static/
        sudo mv $DEPLOY_PATH/admin.html $DEPLOY_PATH/static/ 2>/dev/null || true
        sudo mv $DEPLOY_PATH/favicon.ico $DEPLOY_PATH/static/ 2>/dev/null || true
        
        echo "✅ Structure fixed"
    fi
    
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