#!/usr/bin/env python3
"""
Migration script to add floor field to existing database records
This script will add the floor column to FlatmateInvitation and User tables if not present
"""

import sqlite3
import os
from datetime import datetime

def add_floor_column_to_database():
    """Add floor column to existing database tables"""
    
    # Check if database exists
    db_path = 'apartments.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    print(f"🔄 Starting floor field migration for {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Backup timestamp
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add floor column to FlatmateInvitation table if not exists
        try:
            cursor.execute("ALTER TABLE flatmate_invitations ADD COLUMN floor TEXT")
            print("✅ Added floor column to flatmate_invitations table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Floor column already exists in flatmate_invitations table")
            else:
                raise e
        
        # Add floor column to User table if not exists
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN flat_floor TEXT")
            print("✅ Added flat_floor column to users table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  flat_floor column already exists in users table")
            else:
                raise e
        
        # Check current table structure
        print("\n📋 Current flatmate_invitations table structure:")
        cursor.execute("PRAGMA table_info(flatmate_invitations)")
        for row in cursor.fetchall():
            print(f"  - {row[1]} ({row[2]})")
        
        print("\n📋 Current users table structure:")
        cursor.execute("PRAGMA table_info(users)")
        for row in cursor.fetchall():
            print(f"  - {row[1]} ({row[2]})")
        
        # Check if there are any records to potentially update
        cursor.execute("SELECT COUNT(*) FROM flatmate_invitations")
        invitation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database statistics:")
        print(f"  - FlatmateInvitation records: {invitation_count}")
        print(f"  - User records: {user_count}")
        
        if invitation_count > 0 or user_count > 0:
            print("\n⚠️  Note: Existing records will have NULL floor values.")
            print("   New invitations will automatically include floor information.")
            print("   Users created through new invitations will inherit floor from invitation.")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"✅ Floor field support has been added to the database")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🏢 FlatFund Floor Field Migration")
    print("=" * 50)
    
    success = add_floor_column_to_database()
    
    if success:
        print("\n🚀 Migration Summary:")
        print("   • Floor column added to flatmate_invitations table")
        print("   • flat_floor column added to users table") 
        print("   • Indian floor conventions supported ('B', 'G', '1', '2', etc.)")
        print("   • New invitations will include floor information")
        print("   • New users will inherit floor from invitations")
        print("\n✅ Your database is now ready for floor-based apartment management!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
