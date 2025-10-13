#!/usr/bin/env python3
"""
Test script for student sign-in functionality.
"""
import requests
import json

# Updated URLs for the new ports
DJANGO_URL = 'http://127.0.0.1:8001'
REACT_URL = 'http://localhost:3000'

def test_django_server():
    """Test if Django server is running."""
    print("🧪 Testing Django server...")
    try:
        response = requests.get(f'{DJANGO_URL}/')
        if response.status_code == 200:
            print("✅ Django server is running!")
            return True
        else:
            print(f"❌ Django server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Django server error: {e}")
        return False

def test_demo_login():
    """Test demo login functionality."""
    print("\n🧪 Testing demo login...")
    try:
        response = requests.post(
            f'{DJANGO_URL}/api/users/demo/login/',
            json={
                'email': 'test.student@example.com',
                'first_name': 'Test',
                'last_name': 'Student'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Demo login working!")
            print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Token: {data['access_token'][:20]}...")
            return True
        else:
            print(f"❌ Demo login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Demo login error: {e}")
        return False

def test_oauth_url():
    """Test OAuth URL endpoint."""
    print("\n🧪 Testing OAuth URL endpoint...")
    try:
        response = requests.get(f'{DJANGO_URL}/api/users/oauth/google/url/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('demo_mode'):
                print("✅ OAuth URL endpoint working (demo mode)")
                print(f"   Message: {data.get('message', 'N/A')}")
            else:
                print("✅ OAuth URL endpoint working (production mode)")
            return True
        else:
            print(f"❌ OAuth URL endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OAuth URL endpoint error: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints."""
    print("\n🧪 Testing API endpoints...")
    
    endpoints = [
        ('/api/', 'API Documentation'),
        ('/admin/', 'Admin Interface'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'{DJANGO_URL}{endpoint}')
            if response.status_code in [200, 302]:  # 302 for admin redirect
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def main():
    """Run all tests."""
    print("🚀 Testing Student Sign-In System")
    print("=" * 50)
    
    # Test Django server
    django_ok = test_django_server()
    
    if django_ok:
        # Test API endpoints
        test_api_endpoints()
        
        # Test authentication
        demo_ok = test_demo_login()
        oauth_ok = test_oauth_url()
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"   Django Server: {'✅ PASS' if django_ok else '❌ FAIL'}")
        print(f"   Demo Login: {'✅ PASS' if demo_ok else '❌ FAIL'}")
        print(f"   OAuth URL: {'✅ PASS' if oauth_ok else '❌ FAIL'}")
        
        if django_ok and demo_ok and oauth_ok:
            print("\n🎉 Student sign-in system is working!")
            print("\n📝 How to access:")
            print(f"   1. Django Server: {DJANGO_URL}")
            print(f"   2. React Frontend: {REACT_URL}")
            print(f"   3. Admin Panel: {DJANGO_URL}/admin/")
            print("\n🎓 Students can now sign in using the demo login!")
        else:
            print("\n⚠️  Some tests failed. Check the configuration.")
    else:
        print("\n❌ Django server is not running. Please start it first.")
        print("   Command: source venv/bin/activate && python manage.py runserver 8001")

if __name__ == '__main__':
    main()


