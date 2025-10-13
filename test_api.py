#!/usr/bin/env python3
"""
Simple test script to verify the Django API is working.
"""
import requests
import json
import time

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Django API...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/admin/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Test 2: Test content API (should require authentication)
    try:
        response = requests.get(f"{base_url}/api/content/", timeout=5)
        print(f"✅ Content API endpoint accessible (Status: {response.status_code})")
        if response.status_code == 401:
            print("   (Authentication required - this is expected)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Content API error: {e}")
    
    # Test 3: Test admin interface
    try:
        response = requests.get(f"{base_url}/admin/", timeout=5)
        print(f"✅ Admin interface accessible (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin interface error: {e}")
    
    print("\n🎉 Basic API tests completed!")
    print(f"📊 Admin interface: {base_url}/admin/")
    print(f"📊 API endpoints: {base_url}/api/")
    print("\n📝 Next steps:")
    print("1. Configure Google OAuth2 credentials in .env file")
    print("2. Set up OpenAI API key for content generation")
    print("3. Install and configure Redis for Celery")
    print("4. Build React frontend")
    
    return True

if __name__ == "__main__":
    test_api()
