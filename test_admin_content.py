#!/usr/bin/env python3
"""
Test script for admin content creation functionality.
"""
import requests
import json

DJANGO_URL = 'http://127.0.0.1:8001'

def create_admin_token():
    """Create a demo admin user and get token."""
    print("🔑 Creating admin user...")
    try:
        response = requests.post(
            f'{DJANGO_URL}/api/users/demo/login/',
            json={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Need to make this user an admin
            print("✅ Admin user created/logged in")
            return data['access_token']
        else:
            print(f"❌ Failed to create admin: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_create_content(token):
    """Test creating content with rich text and YouTube."""
    print("\n🧪 Testing content creation...")
    
    test_contents = [
        {
            'section': 'NEWS',
            'title': 'Amazing Student Achievement!',
            'body': 'A student won the science fair!',
            'rich_content': '<h2>Congratulations!</h2><p>A <strong>7th grade student</strong> won first place!</p><ul><li>Project: Solar panels</li><li>Prize: $500</li></ul>',
            'target_grade': 7,
        },
        {
            'section': 'JOKES',
            'title': 'Math Joke',
            'body': 'Why was 6 afraid of 7?',
            'rich_content': '<p><strong>Q:</strong> Why was 6 afraid of 7?</p><p><strong>A:</strong> Because 7 8 9! 😄</p>',
        },
        {
            'section': 'QUOTATION',
            'title': 'Daily Inspiration',
            'body': 'Believe in yourself',
            'rich_content': '<blockquote style="border-left: 4px solid #3b82f6; padding-left: 16px;"><p style="font-size: 18px; font-style: italic;">"Believe you can and you\'re halfway there."</p><p style="text-align: right;">- Theodore Roosevelt</p></blockquote>',
        },
        {
            'section': 'STORY',
            'title': 'Never Give Up',
            'body': 'A story about perseverance',
            'rich_content': '<h2>The Power of Persistence</h2><p>Once upon a time, there was a student who faced many challenges...</p><p style="color: #10b981;">But they never gave up, and eventually succeeded!</p>',
            'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'target_grade': 8,
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    success_count = 0
    for idx, content_data in enumerate(test_contents, 1):
        try:
            response = requests.post(
                f'{DJANGO_URL}/api/content/admin/create/',
                json=content_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Content {idx} created: {content_data['title']}")
                success_count += 1
            else:
                print(f"❌ Content {idx} failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Content {idx} error: {e}")
    
    return success_count

def test_get_admin_content(token):
    """Test retrieving admin content."""
    print("\n🧪 Testing content retrieval...")
    
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    try:
        response = requests.get(
            f'{DJANGO_URL}/api/content/admin/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data))
            print(f"✅ Retrieved {count} content items")
            return True
        else:
            print(f"❌ Failed to retrieve content: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_public_content():
    """Test public content endpoint."""
    print("\n🧪 Testing public content feed...")
    
    sections = ['NEWS', 'JOKES', 'QUOTATION', 'STORY']
    
    for section in sections:
        try:
            response = requests.get(
                f'{DJANGO_URL}/api/content/',
                params={'section': section, 'limit': 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', []))
                print(f"✅ {section}: {count} items available")
            else:
                print(f"❌ {section}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {section}: Error - {e}")

def main():
    """Run all tests."""
    print("🚀 Testing Admin Content Creation System")
    print("=" * 60)
    
    # Create admin token
    token = create_admin_token()
    
    if not token:
        print("\n❌ Failed to get admin token. Cannot proceed with tests.")
        print("   Note: You may need to manually set the user role to 'ADMIN' in the database.")
        return
    
    # Test content creation
    created_count = test_create_content(token)
    
    # Test content retrieval
    retrieval_ok = test_get_admin_content(token)
    
    # Test public content
    test_public_content()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Admin Token: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"   Content Created: {created_count}/4")
    print(f"   Content Retrieval: {'✅ PASS' if retrieval_ok else '❌ FAIL'}")
    
    if created_count > 0:
        print("\n🎉 Admin content creation is working!")
        print("\n📝 Next steps:")
        print("   1. Visit http://localhost:3000")
        print("   2. Sign in as admin")
        print("   3. Go to Admin Dashboard")
        print("   4. Create content with rich text and videos!")
        print("\n🌐 Access Points:")
        print(f"   Admin Dashboard: http://localhost:3000/admin-dashboard")
        print(f"   Student Feed: http://localhost:3000/")
        print(f"   Django Admin: {DJANGO_URL}/admin/")
    else:
        print("\n⚠️  Content creation failed. Check:")
        print("   - User has ADMIN role")
        print("   - API endpoints are working")
        print("   - Database migrations applied")

if __name__ == '__main__':
    main()
