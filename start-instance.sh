#!/bin/bash

# Script to start EC2 instance manually
# Usage: ./start-instance.sh

set -e

echo "🚀 Starting FlatFund EC2 Instance"
echo "=================================="

# Configuration
INSTANCE_ID="i-01972c407dd494e7e"
RDS_INSTANCE_ID="flatfund-db"

echo "📋 Current instance status:"
aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].{State:State.Name,IP:PublicIpAddress}' --output table

echo ""
echo "🚀 Starting EC2 instance..."
aws ec2 start-instances --instance-ids $INSTANCE_ID

echo "🚀 Starting RDS instance..."
aws rds start-db-instance --db-instance-identifier $RDS_INSTANCE_ID

echo ""
echo "⏳ Instance is starting... Waiting for it to be ready..."
echo "📡 Checking instance status..."

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

echo ""
echo "✅ Instance is now running!"
echo "📋 Final status:"
aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].{State:State.Name,IP:PublicIpAddress}' --output table

echo ""
echo "🌐 Your application should be available at:"
echo "   https://flatfund.duckdns.org/static/admin.html"
echo "   https://flatfund.duckdns.org/api/v1/apartments/"
echo ""
echo "💡 Give it 2-3 minutes for Docker containers to fully start up!"
