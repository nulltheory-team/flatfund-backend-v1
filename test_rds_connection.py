#!/usr/bin/env python3
"""
Script to test AWS RDS PostgreSQL connectivity
"""
import psycopg2
import sys
from datetime import datetime

def test_rds_connection():
    """Test connection to AWS RDS PostgreSQL database"""
    
    # RDS connection parameters
    host = "flatfund-db.ctqftasebvp9.ap-south-1.rds.amazonaws.com"
    port = 5432
    database = "postgres"
    username = "postgres"
    password = "yvnreddy2002"
    
    print(f"🔍 Testing connection to AWS RDS...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   Username: {username}")
    print(f"   Time: {datetime.now()}")
    print()
    
    try:
        print("⏳ Attempting to connect...")
        
        # Create connection
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=10  # 10 seconds timeout
        )
        
        print("✅ Connection successful!")
        
        # Test a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL version: {version}")
        
        # Test if the apartments table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'apartments'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("📋 'apartments' table exists")
            
            # Count existing apartments
            cursor.execute("SELECT COUNT(*) FROM apartments;")
            count = cursor.fetchone()[0]
            print(f"🏢 Current apartment count: {count}")
        else:
            print("⚠️  'apartments' table does not exist (will be created on first run)")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 RDS connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Possible solutions:")
        print("   1. Check if RDS instance is running")
        print("   2. Verify security group allows connections from your IP")
        print("   3. Confirm RDS endpoint and credentials are correct")
        print("   4. Check if you're on the right VPC/network")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_rds_connection()
    sys.exit(0 if success else 1)
