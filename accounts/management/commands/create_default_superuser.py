# accounts/management/commands/create_default_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create default superuser if not exists'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            username = 'admin'
            email = 'admin@projecthub.com'
            password = 'changeme123'  # Change this on first login
            
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Default superuser created: {username}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Superuser already exists'))