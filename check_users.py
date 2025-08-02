#!/usr/bin/env python3
"""
Script to check user details and identify the issue with flat_number/flat_floor
"""

import sqlite3
import sys

def check_user_details():
    try:
        conn = sqlite3.connect('apartments.db')
        cursor = conn.cursor()
        
        print("=" * 60)
        print("CHECKING USER RECORDS")
        print("=" * 60)
        
        # Check users table schema
        cursor.execute('PRAGMA table_info(users)')
        columns = cursor.fetchall()
        print("\n📋 users table schema:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        print("\n" + "=" * 60)
        
        # Find users with your email
        cursor.execute('''
            SELECT id, flat_id, user_email_id, user_name, user_phone_number,
                   flat_number, flat_floor, apartment_id, role, created_at
            FROM users 
            WHERE user_email_id = ?
        ''', ('y.sandeepkumarreddy@gmail.com',))
        
        users = cursor.fetchall()
        
        if users:
            print(f"✅ FOUND {len(users)} USER(S) with email: y.sandeepkumarreddy@gmail.com")
            print("-" * 80)
            
            for i, user in enumerate(users, 1):
                print(f"\n👤 USER #{i}:")
                print(f"   ID:              {user[0]}")
                print(f"   Flat ID:         {user[1]}")
                print(f"   Email:           {user[2]}")
                print(f"   Name:            {user[3] or 'NULL ❌'}")
                print(f"   Phone:           {user[4] or 'NULL ❌'}")
                print(f"   Flat Number:     {user[5] or 'NULL ❌'}")
                print(f"   Flat Floor:      {user[6] or 'NULL ❌'}")
                print(f"   Apartment ID:    {user[7]}")
                print(f"   Role:            {user[8]}")
                print(f"   Created At:      {user[9]}")
                
                # Calculate is_all_user_details_filled
                is_complete = bool(
                    user[3] and  # user_name
                    user[4] and  # user_phone_number
                    user[5] is not None and  # flat_number
                    user[6] is not None      # flat_floor
                )
                print(f"   Profile Complete: {'✅ YES' if is_complete else '❌ NO'}")
                
                if not is_complete:
                    missing = []
                    if not user[3]: missing.append("user_name")
                    if not user[4]: missing.append("user_phone_number")  
                    if user[5] is None: missing.append("flat_number")
                    if user[6] is None: missing.append("flat_floor")
                    print(f"   Missing Fields:  {', '.join(missing)}")
        else:
            print("❌ No users found with email: y.sandeepkumarreddy@gmail.com")
        
        # Also check all users to see patterns
        print("\n" + "=" * 60)
        print("🔍 ALL USERS - Summary of flat_number/flat_floor status:")
        print("-" * 80)
        
        cursor.execute('''
            SELECT id, user_email_id, flat_number, flat_floor, role, 
                   CASE 
                       WHEN flat_number IS NULL OR flat_floor IS NULL THEN 'MISSING'
                       ELSE 'COMPLETE'
                   END as flat_status
            FROM users 
            ORDER BY created_at DESC
        ''')
        
        all_users = cursor.fetchall()
        
        print(f"{'ID':<4} {'Email':<30} {'Flat#':<8} {'Floor':<8} {'Role':<8} {'Status'}")
        print("-" * 80)
        
        for user in all_users:
            flat_num = str(user[2]) if user[2] is not None else 'NULL'
            flat_floor = str(user[3]) if user[3] is not None else 'NULL'
            status_icon = '✅' if user[5] == 'COMPLETE' else '❌'
            
            print(f"{user[0]:<4} {user[1]:<30} {flat_num:<8} {flat_floor:<8} {user[4]:<8} {status_icon} {user[5]}")
        
        print("\n" + "=" * 60)
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user_details()
