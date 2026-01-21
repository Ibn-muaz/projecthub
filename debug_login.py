# Debug script to test login functionality
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User as AuthUser

User = get_user_model()

print("Testing authentication...")

# Check if any users exist
users = User.objects.all()
print(f"Total users: {users.count()}")

if users.exists():
    for user in users[:3]:  # Check first 3 users
        print(f"User: {user.username}, Email: {user.email}, Active: {user.is_active}")
        
        # Test authentication
        auth_user = authenticate(username=user.email, password='testpassword')
        if auth_user:
            print(f"  ✓ Authentication successful with email")
        else:
            print(f"  ✗ Authentication failed with email")
            
        auth_user = authenticate(username=user.username, password='testpassword')
        if auth_user:
            print(f"  ✓ Authentication successful with username")
        else:
            print(f"  ✗ Authentication failed with username")
else:
    print("No users found in database")

print("\nTesting completed.")