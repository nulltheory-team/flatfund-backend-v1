#!/bin/bash

# Script to stop EC2 instance manually
# Usage: ./stop-instance.sh

set -e

echo "🛑 Stopping FlatFund EC2 Instance"
echo "=================================="

# Configuration
INSTANCE_ID="i-01972c407dd494e7e"
RDS_INSTANCE_ID="flatfund-db"

echo "📋 Current instance status:"
aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].{State:State.Name,IP:PublicIpAddress}' --output table

echo ""
echo "🛑 Stopping EC2 instance..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID

echo "🛑 Stopping RDS instance..."
aws rds stop-db-instance --db-instance-identifier $RDS_INSTANCE_ID

echo ""
echo "⏳ Instance is stopping... You can check status with:"
echo "   aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name'"
echo ""
echo "💰 Cost Savings: ~$0.50/day when stopped"
echo "🔒 Your Elastic IP (3.111.80.201) will remain the same when you start again!"
