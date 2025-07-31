#!/bin/bash

# Quick deployment script for Flatfund AWS Lambda functions
# Make sure to update the variables below with your actual values

set -e

# Configuration - UPDATE THESE VALUES
AWS_ACCOUNT_ID="951522431634"  # Replace with your AWS account ID
AWS_REGION="ap-south-1"        # Your AWS region (Mumbai)
EC2_INSTANCE_ID="i-01972c407dd494e7e"  # Your actual EC2 instance ID
RDS_INSTANCE_ID="ctqftasebvp9"  # Your actual RDS instance identifier

echo "🚀 Starting Flatfund Lambda Deployment..."
echo "Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "EC2 Instance: $EC2_INSTANCE_ID"
echo "RDS Instance: $RDS_INSTANCE_ID"

# Update instance IDs in Python files
echo "📝 Updating instance IDs in Lambda functions..."
sed -i.bak "s/i-0123456789abcdef0/$EC2_INSTANCE_ID/g" start-instances.py
sed -i.bak "s/flatfund-db/$RDS_INSTANCE_ID/g" start-instances.py
sed -i.bak "s/i-0123456789abcdef0/$EC2_INSTANCE_ID/g" stop-instances.py
sed -i.bak "s/flatfund-db/$RDS_INSTANCE_ID/g" stop-instances.py

# Create IAM Role
echo "🔐 Creating IAM role..."
aws iam create-role \
    --role-name FlatfundInstanceSchedulerRole \
    --assume-role-policy-document file://lambda-trust-policy.json \
    --region $AWS_REGION || echo "Role might already exist"

# Attach policies
echo "📋 Attaching policies to role..."
aws iam attach-role-policy \
    --role-name FlatfundInstanceSchedulerRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name FlatfundInstanceSchedulerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-role-policy \
    --role-name FlatfundInstanceSchedulerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

# Wait for role to propagate
echo "⏳ Waiting for IAM role to propagate..."
sleep 10

# Create deployment packages
echo "📦 Creating deployment packages..."
zip -q start-instances.zip start-instances.py
zip -q stop-instances.zip stop-instances.py

# Create Lambda functions
echo "⚡ Creating Lambda functions..."
aws lambda create-function \
    --function-name flatfund-start-instances \
    --runtime python3.9 \
    --role arn:aws:iam::$AWS_ACCOUNT_ID:role/FlatfundInstanceSchedulerRole \
    --handler start-instances.lambda_handler \
    --zip-file fileb://start-instances.zip \
    --timeout 60 \
    --region $AWS_REGION \
    --description "Start EC2 and RDS instances at 4PM and 10PM IST" || echo "Start function might already exist"

aws lambda create-function \
    --function-name flatfund-stop-instances \
    --runtime python3.9 \
    --role arn:aws:iam::$AWS_ACCOUNT_ID:role/FlatfundInstanceSchedulerRole \
    --handler stop-instances.lambda_handler \
    --zip-file fileb://stop-instances.zip \
    --timeout 60 \
    --region $AWS_REGION \
    --description "Stop EC2 and RDS instances at 7PM and 1AM IST" || echo "Stop function might already exist"

# Create EventBridge rules
echo "⏰ Creating scheduled rules..."

# Start at 4:00 PM IST (10:30 UTC)
aws events put-rule \
    --name flatfund-start-4pm \
    --schedule-expression "cron(30 10 * * ? *)" \
    --description "Start instances at 4:00 PM IST" \
    --region $AWS_REGION

# Stop at 7:00 PM IST (13:30 UTC)
aws events put-rule \
    --name flatfund-stop-7pm \
    --schedule-expression "cron(30 13 * * ? *)" \
    --description "Stop instances at 7:00 PM IST" \
    --region $AWS_REGION

# Start at 10:00 PM IST (16:30 UTC)
aws events put-rule \
    --name flatfund-start-10pm \
    --schedule-expression "cron(30 16 * * ? *)" \
    --description "Start instances at 10:00 PM IST" \
    --region $AWS_REGION

# Stop at 1:00 AM IST (19:30 UTC)
aws events put-rule \
    --name flatfund-stop-1am \
    --schedule-expression "cron(30 19 * * ? *)" \
    --description "Stop instances at 1:00 AM IST" \
    --region $AWS_REGION

# Add Lambda permissions and targets
echo "🎯 Setting up event targets..."

# Start 4PM
aws lambda add-permission \
    --function-name flatfund-start-instances \
    --statement-id flatfund-start-4pm \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ACCOUNT_ID:rule/flatfund-start-4pm \
    --region $AWS_REGION || echo "Permission might already exist"

aws events put-targets \
    --rule flatfund-start-4pm \
    --targets "Id"="1","Arn"="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:flatfund-start-instances" \
    --region $AWS_REGION

# Stop 7PM
aws lambda add-permission \
    --function-name flatfund-stop-instances \
    --statement-id flatfund-stop-7pm \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ACCOUNT_ID:rule/flatfund-stop-7pm \
    --region $AWS_REGION || echo "Permission might already exist"

aws events put-targets \
    --rule flatfund-stop-7pm \
    --targets "Id"="1","Arn"="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:flatfund-stop-instances" \
    --region $AWS_REGION

# Start 10PM
aws lambda add-permission \
    --function-name flatfund-start-instances \
    --statement-id flatfund-start-10pm \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ACCOUNT_ID:rule/flatfund-start-10pm \
    --region $AWS_REGION || echo "Permission might already exist"

aws events put-targets \
    --rule flatfund-start-10pm \
    --targets "Id"="1","Arn"="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:flatfund-start-instances" \
    --region $AWS_REGION

# Stop 1AM
aws lambda add-permission \
    --function-name flatfund-stop-instances \
    --statement-id flatfund-stop-1am \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ACCOUNT_ID:rule/flatfund-stop-1am \
    --region $AWS_REGION || echo "Permission might already exist"

aws events put-targets \
    --rule flatfund-stop-1am \
    --targets "Id"="1","Arn"="arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:flatfund-stop-instances" \
    --region $AWS_REGION

echo "✅ Deployment completed!"
echo ""
echo "📋 Summary:"
echo "- Lambda functions created: flatfund-start-instances, flatfund-stop-instances"
echo "- Schedule: 4-7 PM and 10 PM-1 AM IST daily (6 hours total)"
echo "- Expected cost savings: ~75% on EC2 and RDS"
echo ""
echo "🧪 Test the functions manually:"
echo "aws lambda invoke --function-name flatfund-start-instances response.json"
echo "aws lambda invoke --function-name flatfund-stop-instances response.json"
echo ""
echo "📊 Monitor in AWS Console:"
echo "- Lambda Functions: https://console.aws.amazon.com/lambda/"
echo "- EventBridge Rules: https://console.aws.amazon.com/events/"
echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home#logsV2:"
