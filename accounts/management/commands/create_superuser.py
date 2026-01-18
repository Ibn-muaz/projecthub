# accounts/management/commands/create_superuser.py
import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create or reset a superuser account'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Try to find existing admin users
        admin_usernames = ['admin', 'admin@2223', 'administrator', 'superuser']
        admin_user = None
        
        for username in admin_usernames:
            try:
                admin_user = User.objects.get(username=username)
                self.stdout.write(self.style.SUCCESS(f"Found existing user: {username}"))
                break
            except User.DoesNotExist:
                continue
        
        # If no admin found, create one
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin',
                email='jabaltech1@gmail.com',
                password='AdminProjectHub@2223'
            )
            self.stdout.write(self.style.SUCCESS("Created new admin user"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updating existing user: {admin_user.username}"))
        
        # Reset password and permissions
        new_password = "AdminProjectHub@2223"
        admin_user.set_password(new_password)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        
        # Display credentials
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("✅ SUPERUSER ACCOUNT READY!"))
        self.stdout.write("="*50)
        self.stdout.write(f"Username: {admin_user.username}")
        self.stdout.write(f"Password: {new_password}")
        self.stdout.write(f"Email: {admin_user.email}")
        self.stdout.write("\n" + "="*50)
        self.stdout.write("IMPORTANT: Log in immediately and change this password!")
        self.stdout.write("Access your admin panel at: /admin/")
        self.stdout.write("="*50)
        
        return admin_user.username