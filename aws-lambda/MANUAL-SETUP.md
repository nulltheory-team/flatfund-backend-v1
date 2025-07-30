# 🚀 Flatfund Lambda Deployment - Manual Setup Guide

## Your Current Configuration
- **EC2 Instance ID**: `i-01972c407dd494e7e`
- **RDS Instance ID**: `flatfund-db`
- **AWS Region**: `ap-south-1` (Mumbai)
- **Schedule**: 4-7 PM & 10 PM-1 AM IST (6 hours/day)

## 📋 Step 1: Get Your AWS Account ID

### Option A: From AWS Console
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Click on your username in top-right corner
3. Your 12-digit Account ID is shown in the dropdown

### Option B: From CloudShell (in AWS Console)
1. Go to AWS Console → Search "CloudShell"
2. Run: `aws sts get-caller-identity --query "Account" --output text`

## 📝 Step 2: Update deploy.sh

Once you have your Account ID, edit `deploy.sh` line 8:
```bash
AWS_ACCOUNT_ID="YOUR-12-DIGIT-ACCOUNT-ID"  # Replace with your actual Account ID
```

## 🚀 Step 3: Deploy Using AWS CloudShell

### Upload files to CloudShell:
1. Go to AWS Console → Search "CloudShell"
2. Click "Actions" → "Upload file"
3. Upload these files:
   - `start-instances.py`
   - `stop-instances.py`
   - `deploy.sh`
   - `lambda-trust-policy.json`

### Run deployment:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 🎯 Alternative: Deploy via AWS Console (Manual)

### 1. Create IAM Role
1. Go to IAM → Roles → Create role
2. Choose "AWS service" → "Lambda"
3. Attach these policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEC2FullAccess`
   - `AmazonRDSFullAccess`
4. Name: `FlatfundInstanceSchedulerRole`

### 2. Create Lambda Functions

**Start Function:**
1. Lambda → Create function
2. Name: `flatfund-start-instances`
3. Runtime: Python 3.9
4. Role: `FlatfundInstanceSchedulerRole`
5. Copy code from `start-instances.py`
6. Timeout: 60 seconds

**Stop Function:**
1. Lambda → Create function
2. Name: `flatfund-stop-instances`
3. Runtime: Python 3.9
4. Role: `FlatfundInstanceSchedulerRole`
5. Copy code from `stop-instances.py`
6. Timeout: 60 seconds

### 3. Create EventBridge Rules

**Start at 4:00 PM IST:**
1. EventBridge → Rules → Create rule
2. Name: `flatfund-start-4pm`
3. Schedule: `cron(30 10 * * ? *)` (10:30 UTC = 4:00 PM IST)
4. Target: `flatfund-start-instances`

**Stop at 7:00 PM IST:**
1. EventBridge → Rules → Create rule
2. Name: `flatfund-stop-7pm`
3. Schedule: `cron(30 13 * * ? *)` (13:30 UTC = 7:00 PM IST)
4. Target: `flatfund-stop-instances`

**Start at 10:00 PM IST:**
1. EventBridge → Rules → Create rule
2. Name: `flatfund-start-10pm`
3. Schedule: `cron(30 16 * * ? *)` (16:30 UTC = 10:00 PM IST)
4. Target: `flatfund-start-instances`

**Stop at 1:00 AM IST:**
1. EventBridge → Rules → Create rule
2. Name: `flatfund-stop-1am`
3. Schedule: `cron(30 19 * * ? *)` (19:30 UTC = 1:00 AM IST)
4. Target: `flatfund-stop-instances`

## 🧪 Testing

Test your functions manually:
1. Lambda → Functions → `flatfund-start-instances` → Test
2. Lambda → Functions → `flatfund-stop-instances` → Test

## 💰 Expected Savings

- **Current Cost**: 24/7 operation
- **New Cost**: Only 6 hours/day
- **Savings**: ~75% reduction in EC2 and RDS costs!
- **Lambda Cost**: ~$0.20/month (negligible)

## 📊 Monitoring

- **CloudWatch Logs**: Lambda → Functions → Monitor
- **Instance Status**: EC2/RDS consoles
- **Billing**: Check your AWS billing dashboard after a few days

## ⚠️ Important Notes

1. **RDS takes 5-10 minutes** to start/stop
2. **Test thoroughly** before relying on production
3. **Manual override available** if needed outside schedule
4. **Backup your data** before implementing

Your instances will now automatically:
- ✅ Start at 4:00 PM IST (ready by 4:05 PM)
- ✅ Stop at 7:00 PM IST
- ✅ Start at 10:00 PM IST (ready by 10:05 PM)  
- ✅ Stop at 1:00 AM IST

This gives you exactly 6 hours of operation with maximum cost savings! 🎉
