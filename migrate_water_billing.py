#!/usr/bin/env python3
"""
Database migration script to add water_bill_mode column to apartments table.
Run this script after updating the models to add the new column to existing databases.
"""

import sqlite3
import os

def migrate_database():
    """Add water_bill_mode column to apartments table if it doesn't exist."""
    
    # Use the apartments.db file directly
    db_path = "./apartments.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if water_bill_mode column already exists
        cursor.execute("PRAGMA table_info(apartments);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'water_bill_mode' in columns:
            print("✅ water_bill_mode column already exists in apartments table")
            conn.close()
            return True
        
        # Add the new column
        print("🔄 Adding water_bill_mode column to apartments table...")
        cursor.execute("""
            ALTER TABLE apartments 
            ADD COLUMN water_bill_mode INTEGER NOT NULL DEFAULT 0
        """)
        
        # Commit the changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(apartments);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'water_bill_mode' in columns:
            print("✅ Successfully added water_bill_mode column to apartments table")
            print("   - 0 = Meter based water billing")
            print("   - 1 = Tanker based water billing")
            print("   - Default value: 0 (Meter based)")
            
            # Show current table structure
            print("\n📊 Updated table structure:")
            cursor.execute("PRAGMA table_info(apartments);")
            for column in cursor.fetchall():
                print(f"   - {column[1]} ({column[2]})")
            
            conn.close()
            return True
        else:
            print("❌ Failed to add water_bill_mode column")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FlatFund Database Migration - Add Water Billing Mode")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your application")
        print("2. Test the new water billing mode feature")
        print("3. Verify the admin interface displays the new column")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
