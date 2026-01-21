# Simple authentication test
import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
try:
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")
    sys.exit(1)

# Test authentication
from django.contrib.auth import authenticate
from accounts.models import User

# Check if any users exist
user_count = User.objects.count()
print(f"Total users: {user_count}")

if user_count > 0:
    # Get the first user
    first_user = User.objects.first()
    print(f"First user: {first_user.username} ({first_user.email})")
    
    # Try to authenticate with email
    user = authenticate(username=first_user.email, password='test123')
    if user:
        print("✓ Authentication with email successful")
    else:
        print("✗ Authentication with email failed")
        
    # Try to authenticate with username
    user = authenticate(username=first_user.username, password='test123')
    if user:
        print("✓ Authentication with username successful")
    else:
        print("✗ Authentication with username failed")
else:
    print("No users found in database")

print("Test completed.")