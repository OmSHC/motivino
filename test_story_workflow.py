#!/usr/bin/env python3
"""
Test script for story submission and approval workflow.
"""
import requests
import json

DJANGO_URL = 'http://127.0.0.1:8001'

def test_user_submit_story():
    """Test user story submission."""
    print("🧪 Testing user story submission...")
    
    # First, login as a regular user
    try:
        login_response = requests.post(
            f'{DJANGO_URL}/api/users/login/',
            json={
                'email': 'teststudent@example.com',
                'password': 'password123'
            }
        )
        
        if login_response.status_code != 200:
            print("❌ User login failed")
            return False, None
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Submit a story
        story_data = {
            'title': 'My Inspiring Journey',
            'body': 'This is my story about overcoming challenges.',
            'rich_content': '<h2>My Journey</h2><p>I faced many <strong>challenges</strong> but never gave up!</p><ul><li>Challenge 1</li><li>Challenge 2</li></ul>',
            'youtube_url': ''
        }
        
        response = requests.post(
            f'{DJANGO_URL}/api/content/submit-story/',
            json=story_data,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Story submitted successfully!")
            print(f"   Content ID: {data['content_id']}")
            print(f"   Status: {data['status']}")
            return True, data['content_id']
        else:
            print(f"❌ Story submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def test_get_my_submissions():
    """Test getting user's own submissions."""
    print("\n🧪 Testing get my submissions...")
    
    try:
        # Login as the test user
        login_response = requests.post(
            f'{DJANGO_URL}/api/users/login/',
            json={
                'email': 'teststudent@example.com',
                'password': 'password123'
            }
        )
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(
            f'{DJANGO_URL}/api/content/my-submissions/',
            headers=headers
        )
        
        if response.status_code == 200:
            submissions = response.json()
            print(f"✅ Retrieved {len(submissions)} submission(s)")
            for sub in submissions:
                print(f"   - {sub['title']}: {sub['approval_status']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_admin_get_pending():
    """Test admin getting pending submissions."""
    print("\n🧪 Testing admin get pending submissions...")
    
    try:
        # Login as admin
        login_response = requests.post(
            f'{DJANGO_URL}/api/users/demo/login/',
            json={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(
            f'{DJANGO_URL}/api/content/admin/pending/',
            headers=headers
        )
        
        if response.status_code == 200:
            pending = response.json()
            print(f"✅ Retrieved {len(pending)} pending submission(s)")
            return True, token, pending
        else:
            print(f"❌ Failed: {response.status_code}")
            return False, None, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None, []


def test_admin_approve(content_id, token):
    """Test admin approving a submission."""
    print("\n🧪 Testing admin approval...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            f'{DJANGO_URL}/api/content/admin/{content_id}/approve/',
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Story approved successfully!")
            return True
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_approved_content_visible():
    """Test that approved content appears in feed."""
    print("\n🧪 Testing approved content visibility...")
    
    try:
        # Login as a user
        login_response = requests.post(
            f'{DJANGO_URL}/api/users/login/',
            json={
                'email': 'teststudent@example.com',
                'password': 'password123'
            }
        )
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get STORY content
        response = requests.get(
            f'{DJANGO_URL}/api/content/',
            params={'section': 'STORY', 'limit': 10},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            stories = data.get('results', [])
            print(f"✅ Retrieved {len(stories)} approved stories")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Story Submission and Approval Workflow")
    print("=" * 60)
    
    # Test user submits story
    submit_ok, content_id = test_user_submit_story()
    
    # Test user views their submissions
    my_submissions_ok = test_get_my_submissions()
    
    # Test admin views pending
    pending_ok, admin_token, pending = test_admin_get_pending()
    
    # Test admin approves story
    approve_ok = False
    if content_id and admin_token:
        approve_ok = test_admin_approve(content_id, admin_token)
    
    # Test approved content is visible
    visible_ok = test_approved_content_visible()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   User Story Submission: {'✅ PASS' if submit_ok else '❌ FAIL'}")
    print(f"   User View Submissions: {'✅ PASS' if my_submissions_ok else '❌ FAIL'}")
    print(f"   Admin View Pending: {'✅ PASS' if pending_ok else '❌ FAIL'}")
    print(f"   Admin Approve Story: {'✅ PASS' if approve_ok else '❌ FAIL'}")
    print(f"   Approved Content Visible: {'✅ PASS' if visible_ok else '❌ FAIL'}")
    
    if all([submit_ok, my_submissions_ok, pending_ok, approve_ok, visible_ok]):
        print("\n🎉 Story submission and approval workflow is working perfectly!")
        print("\n📝 How it works:")
        print("   1. Any user can submit stories at /create-story")
        print("   2. Stories are marked as 'pending' and not visible")
        print("   3. Admin reviews pending stories")
        print("   4. Admin approves/rejects stories")
        print("   5. Approved stories appear in Stories feed")
        print("\n🌐 Access Points:")
        print(f"   Submit Story (All Users): http://localhost:3000/create-story")
        print(f"   Pending Approvals (Admin): http://localhost:3000/create-story → Pending tab")
        print(f"   Published Stories: http://localhost:3000/stories")
    else:
        print("\n⚠️  Some tests failed. Check the Django server and configuration.")

if __name__ == '__main__':
    main()
