🚀 AWS RDS Connection Setup Guide
========================================

Your Current Info:
- RDS Endpoint: flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com
- Your Public IP: 103.214.63.45
- Region: ap-south-1 (Mumbai)
- Database: postgres
- Username: postgres

🔧 STEP 1: Check RDS Instance Status
===================================
1. Go to AWS Console: https://console.aws.amazon.com
2. Navigate to: Services → RDS → Databases
3. Find: flatfund-db
4. Check Status: Should show "Available" (not "Stopped")

If STOPPED: Click on the instance → Actions → Start

🔧 STEP 2: Configure Security Group
===================================
1. In RDS instance details, scroll to "Connectivity & security"
2. Click on the Security Group link (e.g., sg-xxxxxxxxx)
3. Select "Inbound rules" tab
4. Click "Edit inbound rules"
5. Add/Modify rule:
   - Type: PostgreSQL
   - Protocol: TCP
   - Port range: 5432
   - Source: Choose one of these options:

   🌐 OPTION A - Your IP Only (Recommended for development):
   Source: My IP (103.214.63.45/32)

   🌍 OPTION B - Allow from anywhere (Less secure):
   Source: Anywhere-IPv4 (0.0.0.0/0)

6. Click "Save rules"

🔧 STEP 3: Verify Public Accessibility
======================================
1. In RDS instance details, check "Connectivity & security"
2. Look for "Public accessibility"
3. Should be: "Yes"

If NO: 
- Click "Modify" button
- Under "Connectivity", change "Public access" to "Yes"
- Click "Continue" → "Modify DB instance"

🔧 STEP 4: Test Connection
==========================
After making changes above, run:
```bash
cd /Users/ysandeepkumarreddy/flatfund-backend-v1
/Users/ysandeepkumarreddy/flatfund-backend-v1/.venv/bin/python test_rds_connection.py
```

🔧 STEP 5: Switch Your App to Use RDS
=====================================
Once connection works, set environment variable:
```bash
export USE_LOCAL_DB=false
```

Then restart your FastAPI server:
```bash
/Users/ysandeepkumarreddy/flatfund-backend-v1/.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

🔧 STEP 6: Verify App Uses RDS
==============================
You should see: "🌐 Using AWS RDS PostgreSQL database" when starting the server

📋 Troubleshooting Checklist
============================
□ RDS instance status is "Available"
□ Security group allows port 5432 from your IP (103.214.63.45)
□ Public accessibility is "Yes"
□ Endpoint is correct: flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com
□ Credentials are correct (postgres/yvnreddy2002)

❗ Common Issues & Solutions
===========================
1. "timeout expired" → Security group not configured
2. "connection refused" → RDS instance is stopped
3. "authentication failed" → Wrong username/password
4. "database does not exist" → Database name typo

📞 Need Help?
=============
Run the test script and share the output:
/Users/ysandeepkumarreddy/flatfund-backend-v1/.venv/bin/python test_rds_connection.py

💡 Pro Tips
===========
- Changes to security groups take effect immediately
- RDS instance modifications may take a few minutes
- Keep your IP updated if it changes (dynamic IP)
- For production, use more restrictive security groups
