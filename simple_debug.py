# Simple debug to check form and user creation
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Check if we can import the form
try:
    from accounts.forms import UserRegistrationForm
    print("✓ Form imported successfully")
except Exception as e:
    print(f"✗ Error importing form: {e}")

# Check if we can import the user model
try:
    from accounts.models import User
    print("✓ User model imported successfully")
    print(f"User model: {User}")
except Exception as e:
    print(f"✗ Error importing User model: {e}")

# Check if we can import the authentication backend
try:
    from accounts.backends import EmailBackend
    print("✓ EmailBackend imported successfully")
except Exception as e:
    print(f"✗ Error importing EmailBackend: {e}")

print("Debug completed.")