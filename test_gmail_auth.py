#!/usr/bin/env python3
"""
Test script for Gmail authentication endpoints.
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_google_oauth_url():
    """Test getting Google OAuth URL."""
    print("🧪 Testing Google OAuth URL endpoint...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/users/oauth/google/url/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OAuth URL endpoint working!")
            print(f"   Auth URL: {data.get('auth_url', 'N/A')[:100]}...")
            print(f"   Client ID: {data.get('client_id', 'N/A')[:20]}...")
            print(f"   Redirect URI: {data.get('redirect_uri', 'N/A')}")
            return True
        else:
            print(f"❌ OAuth URL endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OAuth URL: {e}")
        return False

def test_google_oauth_callback():
    """Test Google OAuth callback endpoint."""
    print("\n🧪 Testing Google OAuth callback endpoint...")
    
    try:
        # Test with invalid code
        response = requests.post(
            f'{BASE_URL}/api/users/oauth/google/callback/',
            json={'code': 'invalid_code'}
        )
        
        if response.status_code == 400:
            print("✅ OAuth callback endpoint working (correctly rejected invalid code)")
            return True
        else:
            print(f"❌ OAuth callback endpoint unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OAuth callback: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints."""
    print("\n🧪 Testing basic API endpoints...")
    
    endpoints = [
        ('/', 'Homepage'),
        ('/api/', 'API Documentation'),
        ('/admin/', 'Admin Interface'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            if response.status_code in [200, 302]:  # 302 for admin redirect
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def main():
    """Run all tests."""
    print("🚀 Testing Gmail Authentication Setup")
    print("=" * 50)
    
    # Test basic endpoints
    test_api_endpoints()
    
    # Test OAuth endpoints
    oauth_url_ok = test_google_oauth_url()
    oauth_callback_ok = test_google_oauth_callback()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   OAuth URL Endpoint: {'✅ PASS' if oauth_url_ok else '❌ FAIL'}")
    print(f"   OAuth Callback Endpoint: {'✅ PASS' if oauth_callback_ok else '❌ FAIL'}")
    
    if oauth_url_ok and oauth_callback_ok:
        print("\n🎉 Gmail authentication setup is working!")
        print("\n📝 Next steps:")
        print("   1. Configure Google OAuth2 credentials in .env file")
        print("   2. Set up Google Cloud Console project")
        print("   3. Test the full OAuth flow in the browser")
        print("   4. Visit http://localhost:3000 to test the frontend")
    else:
        print("\n⚠️  Some tests failed. Check the Django server and configuration.")
    
    print(f"\n🌐 Access Points:")
    print(f"   Django Server: {BASE_URL}")
    print(f"   React Frontend: http://localhost:3000")
    print(f"   Admin Panel: {BASE_URL}/admin/")

if __name__ == '__main__':
    main()


