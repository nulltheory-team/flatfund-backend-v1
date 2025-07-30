# 🔍 Find Your Correct RDS Instance Identifier

## The Issue
Your RDS endpoint is `flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com`, but we need to confirm the exact instance identifier for the Lambda functions.

## Solution: Verify RDS Instance ID in CloudShell

Run this command in AWS CloudShell to get your exact RDS instance identifier:

```bash
# First, try to find RDS instances
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus,Endpoint.Address]' --output table

# If that shows nothing, try RDS clusters
aws rds describe-db-clusters --query 'DBClusters[*].[DBClusterIdentifier,Status,Endpoint]' --output table

# Also check for Aurora clusters specifically
aws rds describe-db-clusters --query 'DBClusters[*].[DBClusterIdentifier,Status,Endpoint,DBClusterMembers[*].DBInstanceIdentifier]' --output table
```

This will show you:
- **DBInstanceIdentifier** (what we need for the Lambda functions)
- **DBInstanceStatus** (current status)
- **Endpoint Address** (the full endpoint you provided)

## Most Likely Scenarios:

### Scenario 1: Single RDS Instance
If you see something like:
```
|  flatfund-db  |  available  |  flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com  |
```
Then use: `RDS_INSTANCE_ID = 'flatfund-db'` ✅

### Scenario 2: RDS Cluster
If you see something like:
```
|  flatfund-db-instance-1  |  available  |  flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com  |
```
Then use: `RDS_INSTANCE_ID = 'flatfund-db-instance-1'`

### Scenario 3: Different Naming
If you see a different identifier, use exactly what appears in the first column.

## Update Your Lambda Functions

Once you know the correct identifier, update it in CloudShell:

**If the identifier is different from 'flatfund-db', update both files:**

```bash
# Update start-instances.py
sed -i "s/RDS_INSTANCE_ID = 'flatfund-db'/RDS_INSTANCE_ID = 'YOUR-ACTUAL-RDS-ID'/g" start-instances.py

# Update stop-instances.py  
sed -i "s/RDS_INSTANCE_ID = 'flatfund-db'/RDS_INSTANCE_ID = 'YOUR-ACTUAL-RDS-ID'/g" stop-instances.py
```

## Quick Test
After updating, test the RDS connection:
```bash
aws rds describe-db-instances --db-instance-identifier YOUR-ACTUAL-RDS-ID
```

This should return details about your RDS instance without errors.

## Common RDS Instance Identifier Patterns:
- `flatfund-db` (simple naming)
- `flatfund-db-instance-1` (cluster member)
- `database-1` (AWS default naming)
- `flatfund-database` (descriptive naming)

Run the describe command first to be 100% sure! 🎯
