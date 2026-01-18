#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting deployment process..."

# Install setuptools first (required for drf-yasg on Python 3.12+)
pip install --upgrade pip setuptools

# Install dependencies
pip install -r backend/requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Setup admin user (only runs on first deploy or when needed)
echo "Setting up admin account..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    # Try to find existing admin
    admin_user = None
    for username in ['admin', 'admin@2223', 'administrator']:
        try:
            admin_user = User.objects.get(username=username)
            print(f'Found existing admin: {username}')
            break
        except User.DoesNotExist:
            continue
    
    if not admin_user:
        # Create new admin
        admin_user = User.objects.create_user(
            username='admin',
            email='jabaltech1@gmail.com',
            password='AdminProjectHub@2223'
        )
        print('Created new admin user')
    
    # Ensure admin permissions
    admin_user.set_password('AdminProjectHub@2223')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.save()
    
    print('✅ Admin account ready!')
    print(f'Username: {admin_user.username}')
    print(f'Password: AdminProjectHub@2223')
    print('⚠️  Login at /admin/ and change password immediately!')
    
except Exception as e:
    print(f'⚠️  Admin setup skipped: {e}')
    print('You may need to connect to PostgreSQL directly.')
"

echo "Deployment completed successfully!"