#!/usr/bin/env python3
"""
Script to make a user an admin.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motivation_news.settings')
django.setup()

from apps.users.models import User


def make_admin(email):
    """Make a user an admin."""
    try:
        user = User.objects.get(email=email)
        user.role = 'ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ Successfully made {email} an admin!")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Role: {user.role}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        return True
    except User.DoesNotExist:
        print(f"❌ User with email {email} not found.")
        print("   Please sign up first, then run this script.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_users():
    """List all users."""
    print("\n📋 All Users:")
    print("-" * 60)
    users = User.objects.all().order_by('-date_joined')
    for user in users:
        print(f"   Email: {user.email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Role: {user.role}")
        print(f"   Grade: {user.grade or 'Not set'}")
        print(f"   School: {user.school or 'Not set'}")
        print(f"   Staff: {user.is_staff}")
        print("-" * 60)


def main():
    """Main function."""
    print("🚀 Admin User Management")
    print("=" * 60)
    
    # List all users first
    list_users()
    
    print("\n" + "=" * 60)
    print("💡 To make a user an admin:")
    print("   python make_admin.py <email>")
    print("\n   Example:")
    print("   python make_admin.py om.mca.om@gmail.com")
    print("\n   Or run this script and enter email when prompted:")
    
    email = input("\n📧 Enter email address to make admin (or press Enter to skip): ").strip()
    
    if email:
        make_admin(email)
        print("\n✅ Done! User can now access Admin Dashboard at:")
        print("   http://localhost:3000/admin-dashboard")
    else:
        print("\n💡 Tip: You can also use 'Demo Admin Login' button on the login page!")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Email provided as command line argument
        email = sys.argv[1].strip()
        make_admin(email)
    else:
        # Interactive mode
        main()
