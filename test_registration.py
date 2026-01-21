# Simple test to check user creation
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.forms import UserRegistrationForm
from django.contrib.auth import authenticate

# Test form creation
test_data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password1': 'TestPassword123!',
    'password2': 'TestPassword123!'
}

form = UserRegistrationForm(data=test_data)
print(f"Form is valid: {form.is_valid()}")

if form.is_valid():
    user = form.save()
    print(f"User created: {user.username}, Email: {user.email}")
    print(f"Password check: {user.check_password('TestPassword123!')}")
    
    # Test authentication
    auth_user = authenticate(username='test@example.com', password='TestPassword123!')
    print(f"Authentication with email: {auth_user is not None}")
    
    auth_user = authenticate(username='testuser', password='TestPassword123!')
    print(f"Authentication with username: {auth_user is not None}")
else:
    print("Form errors:")
    for field, errors in form.errors.items():
        print(f"{field}: {errors}")