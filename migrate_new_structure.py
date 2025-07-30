#!/usr/bin/env python3
"""
Database migration script to create new apartment table structure.
This will create a backup of the existing database and create a new table structure.
"""

import sqlite3
import os
import shutil
from datetime import datetime

def migrate_database():
    """Create new database structure according to the specification."""
    
    db_path = "./apartments.db"
    
    # Create backup
    if os.path.exists(db_path):
        backup_path = f"./apartments_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing table
        cursor.execute("DROP TABLE IF EXISTS apartments;")
        print("🗑️  Dropped existing apartments table")
        
        # Create new table structure
        cursor.execute("""
            CREATE TABLE apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartment_id INTEGER,
                apartment_uuid TEXT UNIQUE NOT NULL,
                apartment_name TEXT NOT NULL,
                apartment_address TEXT NOT NULL,
                admin_email TEXT NOT NULL,
                total_floors INTEGER,
                total_flats INTEGER,
                water_bill_mode INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_apartment_id ON apartments(apartment_id);")
        cursor.execute("CREATE UNIQUE INDEX idx_apartment_uuid ON apartments(apartment_uuid);")
        
        # Commit the changes
        conn.commit()
        
        print("✅ Successfully created new apartments table structure:")
        print("   - id: INTEGER PRIMARY KEY AUTOINCREMENT")
        print("   - apartment_id: INTEGER")
        print("   - apartment_uuid: TEXT UNIQUE (for public API access)")
        print("   - apartment_name: TEXT NOT NULL")
        print("   - apartment_address: TEXT NOT NULL")
        print("   - admin_email: TEXT NOT NULL")
        print("   - total_floors: INTEGER")
        print("   - total_flats: INTEGER")
        print("   - water_bill_mode: INTEGER DEFAULT 0 (0=Meter, 1=Tanker)")
        print("   - created_at: DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Show table info
        cursor.execute("PRAGMA table_info(apartments);")
        print("\n📊 Table structure:")
        for column in cursor.fetchall():
            print(f"   - {column[1]} ({column[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FlatFund Database Migration - New Table Structure")
    print("=" * 65)
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your application")
        print("2. Test the new apartment creation with all fields")
        print("3. Verify the admin interface displays all columns")
        print("4. The apartment_id will now be auto-incrementing integers")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
