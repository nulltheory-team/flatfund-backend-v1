#!/usr/bin/env python3
"""
Migration script to convert flat_floor from INTEGER to TEXT to support Indian floor conventions
"""

import sqlite3
import os
from datetime import datetime

def convert_floor_column_to_text():
    """Convert flat_floor column from INTEGER to TEXT"""
    
    # Check if database exists
    db_path = 'apartments.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    print(f"🔄 Converting flat_floor column to TEXT for Indian floor conventions")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create backup timestamp
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Check current column type
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        flat_floor_column = None
        for col in columns:
            if col[1] == 'flat_floor':
                flat_floor_column = col
                break
        
        if flat_floor_column:
            current_type = flat_floor_column[2]
            print(f"📋 Current flat_floor column type: {current_type}")
            
            if current_type.upper() == 'TEXT':
                print("✅ flat_floor column is already TEXT type - no conversion needed!")
                return True
        
        print("🔄 Converting flat_floor from INTEGER to TEXT...")
        
        # SQLite doesn't support ALTER COLUMN TYPE directly, so we need to:
        # 1. Create new table with correct schema
        # 2. Copy data
        # 3. Drop old table
        # 4. Rename new table
        
        # Create new table with TEXT flat_floor
        cursor.execute("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flat_uuid CHAR(36) UNIQUE DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
                flat_id VARCHAR,
                apartment_uuid CHAR(36),
                apartment_id VARCHAR,
                user_name VARCHAR,
                user_phone_number VARCHAR,
                user_email_id VARCHAR,
                flat_number VARCHAR,
                flat_floor TEXT,  -- Changed from INTEGER to TEXT
                role VARCHAR(6) CHECK (role IN ('ADMIN', 'OWNER', 'TENANT')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy data from old table, converting INTEGER floor values to TEXT
        cursor.execute("""
            INSERT INTO users_new (
                id, flat_uuid, flat_id, apartment_uuid, apartment_id, 
                user_name, user_phone_number, user_email_id, flat_number, 
                flat_floor, role, created_at, updated_at
            )
            SELECT 
                id, flat_uuid, flat_id, apartment_uuid, apartment_id,
                user_name, user_phone_number, user_email_id, flat_number,
                CASE 
                    WHEN flat_floor IS NULL THEN NULL
                    ELSE CAST(flat_floor AS TEXT)
                END as flat_floor,
                role, created_at, updated_at
            FROM users
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE users")
        
        # Rename new table
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        print("✅ Successfully converted flat_floor column to TEXT")
        
        # Verify the conversion
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n📋 Updated users table structure:")
        for row in columns:
            col_info = f"  - {row[1]} ({row[2]})"
            if row[1] == 'flat_floor':
                col_info += " ✨ (Updated!)"
            print(col_info)
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE flat_floor IS NOT NULL")
        users_with_floor = cursor.fetchone()[0]
        
        print(f"\n📊 Data integrity check:")
        print(f"  - Total users: {user_count}")
        print(f"  - Users with floor data: {users_with_floor}")
        
        # Show sample floor values
        cursor.execute("SELECT flat_number, flat_floor FROM users WHERE flat_floor IS NOT NULL LIMIT 5")
        sample_floors = cursor.fetchall()
        
        if sample_floors:
            print(f"\n📋 Sample floor values:")
            for flat_num, floor in sample_floors:
                print(f"  - Flat {flat_num}: Floor {floor}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Floor column conversion completed successfully!")
        print(f"✅ flat_floor now supports Indian conventions: 'B', 'G', '1', '2', etc.")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🏢 FlatFund Floor Column Type Conversion")
    print("=" * 60)
    
    success = convert_floor_column_to_text()
    
    if success:
        print("\n🚀 Conversion Summary:")
        print("   • flat_floor column converted from INTEGER to TEXT")
        print("   • Existing numeric floor values preserved as text")
        print("   • Indian floor conventions now supported:")
        print("     - 'B' for Basement")
        print("     - 'G' for Ground Floor") 
        print("     - '1', '2', '3'... for numbered floors")
        print("     - 'M' for Mezzanine (if needed)")
        print("     - 'UG' for Upper Ground (if needed)")
        print("\n✅ Your database now fully supports Indian apartment floor conventions!")
    else:
        print("\n❌ Conversion failed. Please check the errors above.")
