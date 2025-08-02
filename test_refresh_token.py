import requests
import json
import sqlite3
import time
import os
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
DB_PATH = "apartments.db"

# Use a unique email for testing to avoid conflicts
TEST_EMAIL = f"test_user_{int(time.time())}@example.com"

def create_test_apartment():
    """Creates a new apartment for testing and returns its ID."""
    print("\n--- Step 0: Creating a test apartment ---")
    apartment_payload = {
        "apartment_name": "Test Apartment",
        "admin_email": TEST_EMAIL,
        "apartment_address": "123 Test Street"
    }
    try:
        response = requests.post(f"{BASE_URL}/apartments/", json=apartment_payload)
        if response.status_code in [200, 201]:
            apt_data = response.json()
            apt_id = apt_data.get("apartment_id")
            print(f"✅ Test apartment created successfully. Apartment ID: {apt_id}")
            return apt_id
        else:
            print(f"❌ Failed to create apartment. Status: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        return None

def get_latest_otp(email, apt_id):
    """Connects to the database and retrieves the latest OTP for a user."""
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}. Make sure the backend server has been run at least once.")
        return None
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT otp_code FROM otp_verifications WHERE email = ? AND apartment_id = ? ORDER BY created_at DESC LIMIT 1",
            (email, apt_id)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def run_test():
    """Runs the full refresh token test flow."""
    print(f"🚀 Starting refresh token test for user: {TEST_EMAIL}")

    # Step 0: Create a test apartment
    test_apt_id = create_test_apartment()
    if not test_apt_id:
        return

    # Step 1: Request OTP
    print("\n--- Step 1: Requesting OTP ---")
    signin_payload = {"apt_id": test_apt_id, "admin_email": TEST_EMAIL}
    try:
        response = requests.post(f"{BASE_URL}/signin", json=signin_payload)
        if response.status_code == 200:
            print("✅ OTP requested successfully.")
        elif response.status_code == 404:
            print(f"❌ Error: Apartment not found for ID={test_apt_id}. This should not happen after creation.")
            return
        else:
            print(f"❌ Failed to request OTP. Status: {response.status_code}, Response: {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        print("💡 Tip: Make sure your FastAPI server is running on http://127.0.0.1:8000.")
        return

    # Step 2: Retrieve OTP from database
    print("\n--- Step 2: Retrieving OTP from database ---")
    time.sleep(1) # Give the server a moment to commit the OTP to the DB
    otp = get_latest_otp(TEST_EMAIL, test_apt_id)
    if otp:
        print(f"✅ OTP retrieved: {otp}")
    else:
        print("❌ Failed to retrieve OTP from the database.")
        return

    # Step 3: Verify OTP and get tokens
    print("\n--- Step 3: Verifying OTP to get tokens ---")
    verify_payload = {"apt_id": test_apt_id, "admin_email": TEST_EMAIL, "otp": otp}
    response = requests.post(f"{BASE_URL}/verify-otp", json=verify_payload)
    
    if response.status_code != 200:
        print(f"❌ OTP verification failed. Status: {response.status_code}, Response: {response.text}")
        return

    try:
        auth_data = response.json()
        if not auth_data.get("status"):
            print(f"❌ OTP verification failed: {auth_data.get('message')}")
            return
            
        refresh_token = auth_data.get("token", {}).get("refresh_token")
        initial_access_token = auth_data.get("token", {}).get("access_token")

        if not refresh_token or not initial_access_token:
            print("❌ Did not receive tokens upon OTP verification.")
            return
        
        print("✅ OTP verified successfully.")
        print(f"🔑 Initial Access Token (first 15 chars): {initial_access_token[:15]}...")
        print(f"🔄 Refresh Token (first 15 chars): {refresh_token[:15]}...")

    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON from verify-otp response: {response.text}")
        return

    # Step 4: Use Refresh Token to get a new Access Token
    print("\n--- Step 4: Using Refresh Token ---")
    time.sleep(1) # To ensure the new token is different if timestamps are involved
    refresh_payload = {"refresh_token": refresh_token}
    response = requests.post(f"{BASE_URL}/token/refresh", json=refresh_payload)

    if response.status_code != 200:
        print(f"❌ Failed to refresh token. Status: {response.status_code}, Response: {response.text}")
        return

    try:
        new_token_data = response.json()
        new_access_token = new_token_data.get("access_token")
        new_refresh_token = new_token_data.get("refresh_token")

        if not new_access_token or not new_refresh_token:
            print("❌ Refresh endpoint did not return new tokens.")
            return
        
        print("✅ Successfully received new tokens.")
        print(f"🔑 New Access Token (first 15 chars): {new_access_token[:15]}...")
        print(f"🔄 New Refresh Token (first 15 chars): {new_refresh_token[:15]}...")

        if new_access_token == initial_access_token:
            print("⚠️ Warning: New access token is the same as the old one.")
        else:
            print("✅ New access token is different from the old one, as expected.")

        print("\n🎉 Test complete: Refresh token mechanism is working correctly! 🎉")

    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON from token/refresh response: {response.text}")
        return

if __name__ == "__main__":
    run_test()
