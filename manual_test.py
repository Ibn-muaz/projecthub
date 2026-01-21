# Manual test of the registration process
# This will help us identify where the issue might be

print("Starting manual registration test...")

# Step 1: Check if we can access the database
print("Step 1: Checking database access...")

try:
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    import django
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")
    exit(1)

# Step 2: Check User model
try:
    from accounts.models import User
    print("✓ User model imported")
    print(f"User count: {User.objects.count()}")
except Exception as e:
    print(f"✗ User model error: {e}")

# Step 3: Check form
try:
    from accounts.forms import UserRegistrationForm
    print("✓ Registration form imported")
except Exception as e:
    print(f"✗ Form error: {e}")

print("Manual test completed.")