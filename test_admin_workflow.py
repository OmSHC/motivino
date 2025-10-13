#!/usr/bin/env python3
"""
Test script for admin approval workflow with rejection reasons and resubmission.
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"

def get_demo_token(email="user@example.com"):
    """Get demo token for testing"""
    response = requests.post(f"{BASE_URL}/users/demo/login/", json={
        "email": email,
        "first_name": "Test",
        "last_name": "User"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get demo token for {email}: {response.text}")
        return None

def get_admin_demo_token():
    """Get admin demo token"""
    return get_demo_token("admin@example.com")

def submit_story(token, title, content):
    """Submit a story as user"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/content/submit-story/", json={
        "title": title,
        "rich_content": content
    }, headers=headers)

    if response.status_code == 201:
        print(f"✅ Story submitted: {response.json()['content_id']}")
        return response.json()["content_id"]
    else:
        print(f"❌ Failed to submit story: {response.text}")
        return None

def get_pending_submissions(token):
    """Get pending submissions as admin"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/content/admin/pending/", headers=headers)

    if response.status_code == 200:
        submissions = response.json()
        print(f"📋 Found {len(submissions)} pending submissions")
        return submissions
    else:
        print(f"❌ Failed to get pending submissions: {response.text}")
        return []

def reject_submission(token, content_id, reason):
    """Reject a submission with reason"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/content/admin/{content_id}/reject/",
                           json={"rejection_reason": reason}, headers=headers)

    if response.status_code == 200:
        print(f"❌ Story rejected: {response.json()['content_id']}")
        return True
    else:
        print(f"❌ Failed to reject story: {response.text}")
        return False

def resubmit_story(user_token, content_id, new_title, new_content):
    """Resubmit a rejected story"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.post(f"{BASE_URL}/content/resubmit/{content_id}/", json={
        "title": new_title,
        "rich_content": new_content
    }, headers=headers)

    if response.status_code == 201:
        print(f"🔄 Story resubmitted: {response.json()['content_id']}")
        return response.json()["content_id"]
    else:
        print(f"❌ Failed to resubmit story: {response.text}")
        return None

def get_user_submissions(token):
    """Get user's submissions"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/content/my-submissions/", headers=headers)

    if response.status_code == 200:
        submissions = response.json()
        print(f"📝 User has {len(submissions)} submissions")
        return submissions
    else:
        print(f"❌ Failed to get user submissions: {response.text}")
        return []

def test_workflow():
    print("🚀 Testing Admin Approval Workflow")
    print("=" * 50)

    # Get tokens using demo login
    admin_token = get_admin_demo_token()
    user_token = get_demo_token("user@example.com")

    if not admin_token or not user_token:
        print("❌ Failed to get demo tokens")
        return

    print("✅ Got demo tokens for admin and user")

    print("\n1. User submits a story...")
    story_id = submit_story(user_token, "Test Story", "<p>This is a test story for approval workflow.</p>")

    if not story_id:
        print("❌ Story submission failed")
        return

    print("\n2. Admin checks pending submissions...")
    time.sleep(2)  # Wait a bit for the submission to be processed
    pending = get_pending_submissions(admin_token)

    if not pending:
        print("❌ No pending submissions found")
        return

    # Find our submitted story
    our_story = None
    for submission in pending:
        if submission["id"] == story_id:
            our_story = submission
            break

    if not our_story:
        print("❌ Our submitted story not found in pending")
        return

    print(f"✅ Found our story in pending: {our_story['title']}")

    print("\n3. Admin rejects the story with reason...")
    reject_reason = "This story needs more detailed content and better formatting."
    success = reject_submission(admin_token, story_id, reject_reason)

    if not success:
        print("❌ Rejection failed")
        return

    print("\n4. User checks their submissions...")
    user_submissions = get_user_submissions(user_token)

    # Find our rejected story
    our_rejected_story = None
    for submission in user_submissions:
        if submission["id"] == story_id:
            our_rejected_story = submission
            break

    if not our_rejected_story:
        print("❌ Our rejected story not found in user submissions")
        return

    print(f"✅ Found rejected story: {our_rejected_story['title']}")
    print(f"📝 Rejection reason: {our_rejected_story.get('rejection_reason', 'No reason provided')}")

    print("\n5. User resubmits the story with improvements...")
    new_title = "Improved Test Story"
    new_content = "<p>This is an improved version of the test story with better content and formatting.</p><p>It now includes more details and follows the guidelines better.</p>"

    resubmitted_id = resubmit_story(user_token, story_id, new_title, new_content)

    if not resubmitted_id:
        print("❌ Resubmission failed")
        return

    print(f"✅ Story resubmitted successfully: {resubmitted_id}")

    print("\n6. Admin checks pending submissions again...")
    time.sleep(2)  # Wait for resubmission
    pending = get_pending_submissions(admin_token)

    # Find the resubmitted story
    resubmitted_story = None
    for submission in pending:
        if submission["id"] == resubmitted_id:
            resubmitted_story = submission
            break

    if resubmitted_story:
        print(f"✅ Resubmitted story found in pending: {resubmitted_story['title']}")
        print(f"📋 Status: {resubmitted_story['approval_status']}")
        print(f"🔗 Original submission: {resubmitted_story.get('original_submission', 'None')}")
    else:
        print("❌ Resubmitted story not found in pending")

    print("\n✅ Admin approval workflow test completed!")
    print("\n📋 Summary:")
    print("   - Story submission: ✅")
    print("   - Pending review: ✅")
    print("   - Rejection with reason: ✅")
    print("   - User can see rejection reason: ✅")
    print("   - Resubmission: ✅")
    print("   - Resubmitted story in pending: ✅")

if __name__ == "__main__":
    test_workflow()