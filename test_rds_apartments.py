#!/usr/bin/env python3
"""
Test creating apartments with RDS
"""
import requests
import json

def test_rds_apartment_creation():
    """Test creating apartments in RDS"""
    
    base_url = "http://localhost:8000/api/v1/apartments"
    
    # Test apartment
    test_apartment = {
        "apartment_name": "R and P Kalpavriksha",
        "apartment_address": "Dhruva Dhama Layout, Kammasandra Main Rd, Electronic City, Bengaluru, Karnataka 560100",
        "admin_email": "y.sandeepkumarreddy@gmail.com"
    }
    
    print("🧪 Testing RDS Apartment Creation")
    print("=" * 50)
    print(f"API URL: {base_url}")
    print(f"Test apartment: {test_apartment['apartment_name']}")
    print()
    
    try:
        # Get current apartments
        print("1️⃣ Fetching existing apartments...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            existing = response.json()
            print(f"   ✅ Found {len(existing)} existing apartments")
            for apt in existing:
                print(f"      - {apt.get('apartment_id', 'N/A')}: {apt.get('apartment_name', 'N/A')}")
        else:
            print(f"   ⚠️  Could not fetch existing: {response.status_code}")
        
        print("\n2️⃣ Creating new apartment...")
        response = requests.post(f"{base_url}/", json=test_apartment)
        
        if response.status_code == 201:
            apartment = response.json()
            print(f"   ✅ Created successfully!")
            print(f"   🆔 Apartment ID: {apartment['apartment_id']}")
            print(f"   🔑 UUID: {apartment['id']}")
            print(f"   📧 Email: {apartment['admin_email']}")
            
            # Verify it's in the database
            print("\n3️⃣ Verifying in database...")
            response = requests.get(f"{base_url}/")
            if response.status_code == 200:
                all_apartments = response.json()
                print(f"   ✅ Total apartments now: {len(all_apartments)}")
                
                # Find our apartment
                created_apt = next((apt for apt in all_apartments if apt['id'] == apartment['id']), None)
                if created_apt:
                    print(f"   ✅ Found our apartment: {created_apt['apartment_id']}")
                else:
                    print(f"   ❌ Could not find our apartment in list")
            
            return True
            
        else:
            print(f"   ❌ Failed to create: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_rds_apartment_creation()
    if success:
        print("\n🎉 RDS test completed successfully!")
        print("✅ Your RDS database is working perfectly!")
    else:
        print("\n💥 RDS test failed!")
    
    print("\n🌐 Open http://localhost:8000/static/admin.html to see the admin UI")
