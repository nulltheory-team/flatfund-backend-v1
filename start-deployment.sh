#!/bin/bash

# Quick start script for FlatFund Backend deployment

echo "🚀 FlatFund Backend - Quick Start"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   (The directory containing app/main.py)"
    exit 1
fi

echo "1️⃣ Creating deployment package..."
./package-for-deployment.sh

echo ""
echo "2️⃣ Package created successfully!"
echo ""
echo "🎯 Next Steps for AWS Deployment:"
echo "=================================="
echo ""
echo "📦 1. Your deployment package is ready:"
echo "      Location: /tmp/flatfund-backend-*.tar.gz"
echo ""
echo "🌩️  2. Launch AWS EC2 Instance:"
echo "      - Ubuntu 22.04 LTS"
echo "      - t2.micro (free tier)"
echo "      - Security group: SSH(22), HTTP(80), HTTPS(443), Custom(8000)"
echo ""
echo "📤 3. Upload package to EC2:"
echo "      scp -i your-key.pem /tmp/flatfund-backend-*.tar.gz ubuntu@your-ec2-ip:/home/ubuntu/"
echo ""
echo "🚀 4. Deploy on EC2:"
echo "      ssh -i your-key.pem ubuntu@your-ec2-ip"
echo "      tar -xzf flatfund-backend-*.tar.gz"
echo "      cd flatfund-backend-*"
echo "      chmod +x deploy-aws.sh && ./deploy-aws.sh"
echo "      sudo cp -r * /opt/flatfund/"
echo "      cd /opt/flatfund && sudo systemctl start flatfund"
echo ""
echo "🌐 5. Access your app:"
echo "      Admin UI: http://your-ec2-ip/static/admin.html"
echo "      API Docs: http://your-ec2-ip/docs"
echo "      API: http://your-ec2-ip/api/v1/apartments/"
echo ""
echo "📖 For detailed instructions, see AWS-DEPLOYMENT-GUIDE.md"
echo ""
echo "✨ Happy deploying!"
