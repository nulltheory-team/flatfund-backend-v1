#!/usr/bin/env python3
"""
Test script to demonstrate apartment ID generation
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1/apartments"

def test_apartment_creation():
    """Test creating apartments with auto-generated IDs"""
    
    # Test apartment names
    test_apartments = [
        {
            "apartment_name": "R and P Kalpavriksha",
            "apartment_address": "Dhruva Dhama Layout, Kammasandra Main Rd, Shree Ananth Nagar Layout, Glass Factory Layout, Electronic City, Bengaluru, Karnataka 560100",
            "admin_email": "y.sandeepkumarreddy@gmail.com"
        },
        {
            "apartment_name": "Brigade Golden Triangle",
            "apartment_address": "CV Raman Nagar, Bengaluru, Karnataka 560093",
            "admin_email": "admin@brigade.com"
        },
        {
            "apartment_name": "Prestige Lakeside Habitat",
            "apartment_address": "Varthur Road, Whitefield, Bengaluru, Karnataka 560066",
            "admin_email": "admin@prestige.com"
        },
        {
            "apartment_name": "Sobha City",
            "apartment_address": "Thanisandra Road, Bengaluru, Karnataka 560077",
            "admin_email": "admin@sobha.com"
        },
        {
            "apartment_name": "R and P Gardens",  # Similar to first one
            "apartment_address": "Another location, Bengaluru, Karnataka",
            "admin_email": "admin@rpgardens.com"
        }
    ]
    
    print("🧪 Testing Apartment ID Generation")
    print("=" * 50)
    
    created_apartments = []
    
    for i, apartment_data in enumerate(test_apartments, 1):
        print(f"\n{i}. Creating: {apartment_data['apartment_name']}")
        
        try:
            response = requests.post(BASE_URL + "/", json=apartment_data)
            
            if response.status_code == 201:
                apartment = response.json()
                created_apartments.append(apartment)
                print(f"   ✅ Created with ID: {apartment['apartment_id']}")
                print(f"   📧 UUID: {apartment['id']}")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
    
    # Display all created apartments
    if created_apartments:
        print("\n" + "=" * 50)
        print("📋 All Created Apartments:")
        print("=" * 50)
        
        for i, apt in enumerate(created_apartments, 1):
            print(f"{i:2d}. ID: {apt['apartment_id']:15} | Name: {apt['apartment_name']}")
    
    return created_apartments

def get_all_apartments():
    """Get all apartments from the API"""
    try:
        response = requests.get(BASE_URL + "/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get apartments: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return []

if __name__ == "__main__":
    print("🏢 FlatFund Apartment ID Generation Test")
    print("=" * 60)
    
    # Get existing apartments first
    existing = get_all_apartments()
    if existing:
        print(f"📊 Found {len(existing)} existing apartments")
        for apt in existing:
            print(f"   - {apt['apartment_id']}: {apt['apartment_name']}")
    else:
        print("📭 No existing apartments found")
    
    # Test creating new apartments
    created = test_apartment_creation()
    
    print(f"\n🎉 Test completed! Created {len(created)} new apartments.")
    print("\n💡 Open http://localhost:8000/static/admin.html to see the admin UI")
