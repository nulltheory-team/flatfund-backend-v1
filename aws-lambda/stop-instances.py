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
    EC2_INSTANCE_ID = 'i-01972c407dd494e7e'  # Replace with your actual EC2 instance ID
    RDS_INSTANCE_ID = 'flatfund-db'          # Replace with your actual RDS instance identifier
    
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
