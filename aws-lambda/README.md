# AWS Lambda Deployment Guide for EC2/RDS Auto Start/Stop

## 📋 Prerequisites
1. AWS CLI configured with appropriate permissions
2. Your EC2 Instance ID and RDS Instance Identifier
3. Lambda execution role with EC2 and RDS permissions

## 🚀 Step-by-Step Deployment

### 1. Update Instance IDs
Before deploying, update the instance IDs in both Python files:

**In `start-instances.py` and `stop-instances.py`:**
```python
EC2_INSTANCE_ID = 'i-your-actual-instance-id'  # Find this in EC2 console
RDS_INSTANCE_ID = 'your-rds-instance-name'     # Find this in RDS console
```

### 2. Create IAM Role for Lambda

Create a file `lambda-trust-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create the role:
```bash
aws iam create-role \
    --role-name FlatfundInstanceSchedulerRole \
    --assume-role-policy-document file://lambda-trust-policy.json
```

### 3. Attach Policies to Role

```bash
# Basic Lambda execution
aws iam attach-role-policy \
    --role-name FlatfundInstanceSchedulerRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# EC2 permissions
aws iam attach-role-policy \
    --role-name FlatfundInstanceSchedulerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

# RDS permissions
aws iam attach-role-policy \
    --role-name FlatfundInstanceSchedulerRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess
```

### 4. Create Lambda Functions

**Create start-instances Lambda:**
```bash
# Create deployment package
zip start-instances.zip start-instances.py

# Create Lambda function
aws lambda create-function \
    --function-name flatfund-start-instances \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR-ACCOUNT-ID:role/FlatfundInstanceSchedulerRole \
    --handler start-instances.lambda_handler \
    --zip-file fileb://start-instances.zip \
    --timeout 60 \
    --description "Start EC2 and RDS instances at 4PM and 10PM IST"
```

**Create stop-instances Lambda:**
```bash
# Create deployment package
zip stop-instances.zip stop-instances.py

# Create Lambda function
aws lambda create-function \
    --function-name flatfund-stop-instances \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR-ACCOUNT-ID:role/FlatfundInstanceSchedulerRole \
    --handler stop-instances.lambda_handler \
    --zip-file fileb://stop-instances.zip \
    --timeout 60 \
    --description "Stop EC2 and RDS instances at 7PM and 1AM IST"
```

### 5. Create EventBridge Rules (Cron Jobs)

**Start instances at 4:00 PM IST (10:30 UTC):**
```bash
aws events put-rule \
    --name flatfund-start-4pm \
    --schedule-expression "cron(30 10 * * ? *)" \
    --description "Start instances at 4:00 PM IST"

aws lambda add-permission \
    --function-name flatfund-start-instances \
    --statement-id flatfund-start-4pm \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:YOUR-REGION:YOUR-ACCOUNT-ID:rule/flatfund-start-4pm

aws events put-targets \
    --rule flatfund-start-4pm \
    --targets "Id"="1","Arn"="arn:aws:lambda:YOUR-REGION:YOUR-ACCOUNT-ID:function:flatfund-start-instances"
```

**Stop instances at 7:00 PM IST (13:30 UTC):**
```bash
aws events put-rule \
    --name flatfund-stop-7pm \
    --schedule-expression "cron(30 13 * * ? *)" \
    --description "Stop instances at 7:00 PM IST"

aws lambda add-permission \
    --function-name flatfund-stop-instances \
    --statement-id flatfund-stop-7pm \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:YOUR-REGION:YOUR-ACCOUNT-ID:rule/flatfund-stop-7pm

aws events put-targets \
    --rule flatfund-stop-7pm \
    --targets "Id"="1","Arn"="arn:aws:lambda:YOUR-REGION:YOUR-ACCOUNT-ID:function:flatfund-stop-instances"
```

**Start instances at 10:00 PM IST (16:30 UTC):**
```bash
aws events put-rule \
    --name flatfund-start-10pm \
    --schedule-expression "cron(30 16 * * ? *)" \
    --description "Start instances at 10:00 PM IST"

aws lambda add-permission \
    --function-name flatfund-start-instances \
    --statement-id flatfund-start-10pm \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:YOUR-REGION:YOUR-ACCOUNT-ID:rule/flatfund-start-10pm

aws events put-targets \
    --rule flatfund-start-10pm \
    --targets "Id"="1","Arn"="arn:aws:lambda:YOUR-REGION:YOUR-ACCOUNT-ID:function:flatfund-start-instances"
```

**Stop instances at 1:00 AM IST (19:30 UTC):**
```bash
aws events put-rule \
    --name flatfund-stop-1am \
    --schedule-expression "cron(30 19 * * ? *)" \
    --description "Stop instances at 1:00 AM IST"

aws lambda add-permission \
    --function-name flatfund-stop-instances \
    --statement-id flatfund-stop-1am \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:YOUR-REGION:YOUR-ACCOUNT-ID:rule/flatfund-stop-1am

aws events put-targets \
    --rule flatfund-stop-1am \
    --targets "Id"="1","Arn"="arn:aws:lambda:YOUR-REGION:YOUR-ACCOUNT-ID:function:flatfund-stop-instances"
```

## 🕐 Schedule Summary
- **4:00 PM IST**: Start instances
- **7:00 PM IST**: Stop instances (3 hours)
- **10:00 PM IST**: Start instances
- **1:00 AM IST**: Stop instances (3 hours)
- **Total**: 6 hours per day

## 💰 Cost Savings
- **EC2**: ~75% savings (6h vs 24h daily)
- **RDS**: ~75% savings (6h vs 24h daily)
- **Lambda**: ~$0.20/month (minimal cost)

## 🔧 Testing
Test the functions manually:
```bash
aws lambda invoke \
    --function-name flatfund-start-instances \
    response.json

aws lambda invoke \
    --function-name flatfund-stop-instances \
    response.json
```

## 📊 Monitoring
- Check CloudWatch Logs for function execution
- Monitor EC2 and RDS instance states
- Set up SNS notifications for failures (optional)

## ⚠️ Important Notes
1. Replace `YOUR-ACCOUNT-ID` and `YOUR-REGION` with actual values
2. Update instance IDs in the Python files
3. RDS instances can take 5-10 minutes to start/stop
4. Test thoroughly before relying on production workloads
