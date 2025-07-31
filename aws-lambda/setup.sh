#!/bin/bash

echo "🔍 Flatfund AWS Setup Helper"
echo "=============================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    echo ""
    exit 1
fi

# Check if AWS CLI is configured
if ! aws configure list &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    echo ""
    echo "You'll need:"
    echo "- AWS Access Key ID"
    echo "- AWS Secret Access Key"
    echo "- Default region: ap-south-1"
    echo "- Default output format: json"
    echo ""
    exit 1
fi

echo "✅ AWS CLI is configured!"
echo ""

# Get Account ID
echo "🔍 Getting your AWS Account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)

if [ $? -eq 0 ]; then
    echo "✅ AWS Account ID: $ACCOUNT_ID"
    
    # Update deploy.sh with actual account ID
    sed -i.bak "s/123456789012/$ACCOUNT_ID/g" deploy.sh
    echo "✅ Updated deploy.sh with your Account ID"
    echo ""
    
    echo "📋 Your Configuration:"
    echo "- AWS Account ID: $ACCOUNT_ID"
    echo "- AWS Region: ap-south-1"
    echo "- EC2 Instance ID: i-01972c407dd494e7e"
    echo "- RDS Instance ID: flatfund-db"
    echo ""
    
    echo "🚀 Ready to deploy! Run:"
    echo "   chmod +x deploy.sh"
    echo "   ./deploy.sh"
    echo ""
    
    echo "📊 Expected Schedule (IST):"
    echo "- 4:00 PM - 7:00 PM (3 hours)"
    echo "- 10:00 PM - 1:00 AM (3 hours)"
    echo "- Total: 6 hours/day = 75% cost savings! 💰"
    
else
    echo "❌ Failed to get AWS Account ID. Please check your AWS credentials."
    exit 1
fi
