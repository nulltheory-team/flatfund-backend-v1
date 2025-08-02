#!/usr/bin/env python3
"""
Script to check invitation details for UUID: 801239d5-3e95-4fda-8e0b-d876ce4028a6
"""

import sqlite3
import sys
from datetime import datetime

def check_invitation():
    invitation_uuid = '801239d5-3e95-4fda-8e0b-d876ce4028a6'
    
    try:
        # Connect to the database
        conn = sqlite3.connect('apartments.db')
        cursor = conn.cursor()
        
        print("=" * 60)
        print("CHECKING INVITATION RECORD")
        print("=" * 60)
        
        # First, check the schema of flatmate_invitations table
        cursor.execute('PRAGMA table_info(flatmate_invitations)')
        columns = cursor.fetchall()
        print("\n📋 flatmate_invitations table schema:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        print("\n" + "=" * 60)
        
        # Look for the specific invitation UUID
        cursor.execute('''
            SELECT * FROM flatmate_invitations 
            WHERE invitation_uuid = ?
        ''', (invitation_uuid,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ FOUND INVITATION: {invitation_uuid}")
            print("-" * 40)
            
            # Get column names for better display
            cursor.execute('PRAGMA table_info(flatmate_invitations)')
            column_info = cursor.fetchall()
            column_names = [col[1] for col in column_info]
            
            # Display each field with proper formatting
            for i, value in enumerate(result):
                field_name = column_names[i]
                if field_name in ['created_at', 'expires_at', 'used_at'] and value:
                    # Format datetime fields
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        formatted_value = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except:
                        formatted_value = value
                    print(f"   {field_name:20}: {formatted_value}")
                else:
                    print(f"   {field_name:20}: {value}")
            
            # Check if there are any users created from this invitation
            print("\n" + "-" * 40)
            print("🔍 Checking if any user was created from this invitation...")
            
            cursor.execute('''
                SELECT id, flat_id, user_email_id, flat_number, flat_floor, role, created_at
                FROM users 
                WHERE apartment_id = (
                    SELECT apartment_id FROM flatmate_invitations 
                    WHERE invitation_uuid = ?
                ) AND flat_number = (
                    SELECT flat_number FROM flatmate_invitations 
                    WHERE invitation_uuid = ?
                ) AND user_email_id = (
                    SELECT invited_email FROM flatmate_invitations 
                    WHERE invitation_uuid = ?
                )
            ''', (invitation_uuid, invitation_uuid, invitation_uuid))
            
            user_result = cursor.fetchone()
            
            if user_result:
                print("✅ USER FOUND created from this invitation:")
                print(f"   User ID:     {user_result[0]}")
                print(f"   Flat ID:     {user_result[1]}")
                print(f"   Email:       {user_result[2]}")
                print(f"   Flat Number: {user_result[3]}")
                print(f"   Flat Floor:  {user_result[4]}")
                print(f"   Role:        {user_result[5]}")
                print(f"   Created At:  {user_result[6]}")
            else:
                print("❌ No user found created from this invitation")
        
        else:
            print(f"❌ INVITATION NOT FOUND: {invitation_uuid}")
            
            # Show some recent invitations for reference
            print("\n🔍 Recent invitations in the database:")
            cursor.execute('''
                SELECT invitation_uuid, apartment_id, flat_number, floor, 
                       invited_email, is_used, created_at 
                FROM flatmate_invitations 
                ORDER BY created_at DESC 
                LIMIT 10
            ''')
            
            recent_invitations = cursor.fetchall()
            
            if recent_invitations:
                print("-" * 80)
                print(f"{'UUID (first 8)':<12} {'Apt ID':<8} {'Flat':<6} {'Floor':<6} {'Email':<25} {'Used':<5} {'Created'}")
                print("-" * 80)
                
                for inv in recent_invitations:
                    uuid_short = inv[0][:8] if inv[0] else 'N/A'
                    created_short = inv[6][:16] if inv[6] else 'N/A'
                    print(f"{uuid_short:<12} {inv[1]:<8} {inv[2]:<6} {inv[3]:<6} {inv[4]:<25} {inv[5]:<5} {created_short}")
            else:
                print("   No invitations found in database")
        
        print("\n" + "=" * 60)
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_invitation()
