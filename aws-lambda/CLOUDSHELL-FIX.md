# CloudShell Workaround for "Too Many Requests" Error

## The Issue
AWS CloudShell has rate limits that can cause "Too Many Requests" errors when uploading multiple files quickly.

## Solution: Create Files Directly in CloudShell

Since you have `deploy.sh` and `start-instances.py` uploaded, let's create the missing files directly in CloudShell:

### 1. Get Your AWS Account ID
In CloudShell, run:
```bash
aws sts get-caller-identity --query "Account" --output text
```

### 2. Create the missing files directly in CloudShell:

**Create stop-instances.py:**
```bash
cat > stop-instances.py << 'EOF'
import boto3
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to stop EC2 and RDS instances
    Triggered at 7:00 PM and 1:00 AM IST daily
    """
    
    # Initialize AWS clients
    ec2_client = boto3.client('ec2')
    rds_client = boto3.client('rds')
    
    # Your instance configurations
    EC2_INSTANCE_ID = 'i-01972c407dd494e7e'  # Your actual EC2 instance ID
    RDS_INSTANCE_ID = 'flatfund-db'          # Your actual RDS instance identifier (just the name, not the full endpoint)
    
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'ec2_status': None,
        'rds_status': None,
        'errors': []
    }
    
    try:
        # Stop EC2 instance
        logger.info(f"Stopping EC2 instance: {EC2_INSTANCE_ID}")
        
        # Check EC2 instance current state
        ec2_response = ec2_client.describe_instances(InstanceIds=[EC2_INSTANCE_ID])
        instance_state = ec2_response['Reservations'][0]['Instances'][0]['State']['Name']
        
        if instance_state == 'running':
            ec2_client.stop_instances(InstanceIds=[EC2_INSTANCE_ID])
            results['ec2_status'] = 'stopping'
            logger.info(f"EC2 instance {EC2_INSTANCE_ID} stop command sent")
        elif instance_state == 'stopped':
            results['ec2_status'] = 'already_stopped'
            logger.info(f"EC2 instance {EC2_INSTANCE_ID} is already stopped")
        else:
            results['ec2_status'] = f'current_state_{instance_state}'
            logger.info(f"EC2 instance {EC2_INSTANCE_ID} current state: {instance_state}")
            
    except Exception as e:
        error_msg = f"Error stopping EC2 instance: {str(e)}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        results['ec2_status'] = 'error'
    
    try:
        # Stop RDS instance
        logger.info(f"Stopping RDS instance: {RDS_INSTANCE_ID}")
        
        # Check RDS instance current state
        rds_response = rds_client.describe_db_instances(DBInstanceIdentifier=RDS_INSTANCE_ID)
        db_instance_status = rds_response['DBInstances'][0]['DBInstanceStatus']
        
        if db_instance_status == 'available':
            rds_client.stop_db_instance(DBInstanceIdentifier=RDS_INSTANCE_ID)
            results['rds_status'] = 'stopping'
            logger.info(f"RDS instance {RDS_INSTANCE_ID} stop command sent")
        elif db_instance_status == 'stopped':
            results['rds_status'] = 'already_stopped'
            logger.info(f"RDS instance {RDS_INSTANCE_ID} is already stopped")
        else:
            results['rds_status'] = f'current_state_{db_instance_status}'
            logger.info(f"RDS instance {RDS_INSTANCE_ID} current status: {db_instance_status}")
            
    except Exception as e:
        error_msg = f"Error stopping RDS instance: {str(e)}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        results['rds_status'] = 'error'
    
    logger.info(f"Stop instances completed. Results: {results}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(results, indent=2)
    }
EOF
```

**Create lambda-trust-policy.json:**
```bash
cat > lambda-trust-policy.json << 'EOF'
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
EOF
```

### 3. Update deploy.sh with your Account ID
```bash
# Replace YOUR-ACCOUNT-ID with the actual ID from step 1
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
sed -i "s/123456789012/$ACCOUNT_ID/g" deploy.sh
```

### 4. Verify all files are ready
```bash
ls -la
```
You should see:
- deploy.sh ✅
- start-instances.py ✅
- stop-instances.py ✅
- lambda-trust-policy.json ✅

### 5. Deploy!
```bash
chmod +x deploy.sh
./deploy.sh
```

## Alternative: Manual AWS Console Deployment

If CloudShell continues to have issues, you can:

1. **Create IAM Role manually** in AWS Console
2. **Create Lambda functions manually** and copy-paste the Python code
3. **Create EventBridge rules manually** with the cron expressions

The manual process is detailed in the MANUAL-SETUP.md file.

## Quick Test After Deployment

Test your functions:
```bash
aws lambda invoke --function-name flatfund-start-instances response.json
cat response.json
```

This should show your instances starting! 🎉
