#!/usr/bin/env python3
"""
Initialize RDS database with proper table structure
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base

# Set environment to use RDS BEFORE importing
os.environ["USE_LOCAL_DB"] = "false"

from app.database import DATABASE_URL, Base
from app.models import Apartment

def init_rds_database():
    """Initialize the RDS database with correct table structure"""
    
    print("🚀 Initializing RDS Database")
    print("=" * 50)
    print(f"Database URL: {DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print("🔍 Checking current database state...")
        
        # Check if apartments table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'apartments'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if table_exists:
                print("📋 Apartments table exists, checking structure...")
                
                # Check table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'apartments' 
                    ORDER BY ordinal_position;
                """))
                
                columns = result.fetchall()
                print("   Current columns:")
                for col in columns:
                    print(f"     - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
                
                # Check if our expected columns exist
                column_names = [col[0] for col in columns]
                expected_columns = ['id', 'apartment_id', 'apartment_name', 'apartment_address', 'admin_email']
                missing_columns = [col for col in expected_columns if col not in column_names]
                
                if missing_columns:
                    print(f"❌ Missing columns: {missing_columns}")
                    print("🔄 Dropping and recreating table...")
                    
                    # Drop the table
                    conn.execute(text("DROP TABLE IF EXISTS apartments CASCADE;"))
                    conn.commit()
                    print("   ✅ Dropped existing table")
                else:
                    print("   ✅ All expected columns exist")
                    return True
            else:
                print("📭 Apartments table does not exist")
        
        print("🔨 Creating tables with proper structure...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables created successfully!")
        
        # Verify the new structure
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'apartments' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print("\n📋 Final table structure:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        print("\n🎉 RDS database initialization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_rds_database()
    sys.exit(0 if success else 1)
