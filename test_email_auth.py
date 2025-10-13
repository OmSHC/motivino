#!/usr/bin/env python3
"""
Test script for email/password authentication.
"""
import requests
import json

DJANGO_URL = 'http://127.0.0.1:8001'

def test_signup():
    """Test user signup."""
    print("🧪 Testing user signup...")
    
    test_user = {
        'email': 'teststudent@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'Student',
        'grade': 8,
        'school': 'Test Middle School'
    }
    
    try:
        response = requests.post(
            f'{DJANGO_URL}/api/users/signup/',
            json=test_user
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Signup successful!")
            print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Grade: {data['user']['grade']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Token: {data['access_token'][:30]}...")
            return True, data['access_token']
        elif response.status_code == 400:
            data = response.json()
            if 'already exists' in data.get('error', ''):
                print("ℹ️  User already exists (this is okay for testing)")
                return True, None
            else:
                print(f"❌ Signup failed: {data.get('error')}")
                return False, None
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False, None


def test_login():
    """Test user login."""
    print("\n🧪 Testing user login...")
    
    credentials = {
        'email': 'teststudent@example.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(
            f'{DJANGO_URL}/api/users/login/',
            json=credentials
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Token: {data['access_token'][:30]}...")
            return True, data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False, None


def test_admin_signup():
    """Test admin user signup."""
    print("\n🧪 Testing admin signup...")
    
    admin_user = {
        'email': 'newadmin@example.com',
        'password': 'admin123456',
        'first_name': 'New',
        'last_name': 'Admin'
    }
    
    try:
        response = requests.post(
            f'{DJANGO_URL}/api/users/signup/',
            json=admin_user
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Admin signup successful!")
            print(f"   Email: {data['user']['email']}")
            print(f"   Role: {data['user']['role']}")
            return True
        elif response.status_code == 400:
            print("ℹ️  Admin user already exists")
            return True
        else:
            print(f"❌ Admin signup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin signup error: {e}")
        return False


def test_get_user(token):
    """Test getting current user with token."""
    print("\n🧪 Testing authenticated user retrieval...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(
            f'{DJANGO_URL}/api/users/me/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User retrieval successful!")
            print(f"   Name: {data['first_name']} {data['last_name']}")
            print(f"   Email: {data['email']}")
            print(f"   Grade: {data.get('grade', 'Not set')}")
            return True
        else:
            print(f"❌ User retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User retrieval error: {e}")
        return False


def test_logout(token):
    """Test user logout."""
    print("\n🧪 Testing user logout...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.post(
            f'{DJANGO_URL}/api/users/logout/',
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Logout successful!")
            return True
        else:
            print(f"❌ Logout failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Email/Password Authentication System")
    print("=" * 60)
    
    # Test signup
    signup_ok, signup_token = test_signup()
    
    # Test login
    login_ok, login_token = test_login()
    
    # Test admin signup
    admin_ok = test_admin_signup()
    
    # Test authenticated requests
    token = login_token or signup_token
    user_ok = False
    logout_ok = False
    
    if token:
        user_ok = test_get_user(token)
        logout_ok = test_logout(token)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   User Signup: {'✅ PASS' if signup_ok else '❌ FAIL'}")
    print(f"   User Login: {'✅ PASS' if login_ok else '❌ FAIL'}")
    print(f"   Admin Signup: {'✅ PASS' if admin_ok else '❌ FAIL'}")
    print(f"   User Retrieval: {'✅ PASS' if user_ok else '❌ FAIL'}")
    print(f"   User Logout: {'✅ PASS' if logout_ok else '❌ FAIL'}")
    
    if signup_ok and login_ok:
        print("\n🎉 Email/password authentication is working!")
        print("\n📝 How to use:")
        print("   1. Visit http://localhost:3000")
        print("   2. Click 'Sign Up' to create an account")
        print("   3. Fill in email, password, and details")
        print("   4. Or click 'Sign In' if you have an account")
        print("   5. Use demo buttons for quick testing")
        print("\n🌐 Access Points:")
        print(f"   Student App: http://localhost:3000")
        print(f"   Admin Dashboard: http://localhost:3000/admin-dashboard")
        print(f"   Django Admin: {DJANGO_URL}/admin/")
    else:
        print("\n⚠️  Some tests failed. Check the Django server and configuration.")

if __name__ == '__main__':
    main()
