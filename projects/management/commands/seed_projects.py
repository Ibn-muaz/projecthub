
from django.core.management.base import BaseCommand
from projects.models import ProjectMaterial, Department
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed sample projects'

    def handle(self, *args, **options):
        self.stdout.write('Seeding sample projects...')
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write('No superuser found. Creating default admin user...')
            user = User.objects.create_superuser(
                username='admin',
                email='admin@projecthub.com',
                password='adminpassword123'
            )
            self.stdout.write(self.style.SUCCESS('Created default admin user (admin/adminpassword123)'))

        depts = list(Department.objects.all())
        if not depts:
            self.stdout.write(self.style.ERROR('No departments found. Run populate_departments first.'))
            return

        samples = [
            {
                'title': 'Design and Implementation of Prison Management System',
                'file': 'projects/documents/200design-and-implementation-of-prison-management-system-ac0667e8.docx',
                'abstract': 'This project focuses on automating prison records, inmate tracking, and staff management to improve efficiency and security within correctional facilities.'
            },
            {
                'title': 'Design and Implementation of Secondary School Management System',
                'file': 'projects/documents/design-and-implementaion-of-secondary-school-management-system-01cb13f7.docx',
                'abstract': 'A comprehensive system for managing student records, grading, attendance, and administrative tasks in a secondary school environment.'
            },
            {
                'title': 'Designing and Implementing a Comprehensive and User-Friendly Secondary School Portal',
                'file': 'projects/documents/designing-and-implementing-a-comprehensive-and-user-friendly-seconda_F9sWk8P.docx',
                'abstract': 'An interactive portal designed for students, teachers, and parents to access academic resources, results, and school announcements.'
            }
        ]

        count = 0
        for s in samples:
            dept = random.choice(depts)
            project, created = ProjectMaterial.objects.get_or_create(
                title=s['title'],
                defaults={
                    'slug': slugify(s['title']),
                    'abstract': s['abstract'],
                    'department': dept,
                    'year': 2024,
                    'price': 5000.00,
                    'status': ProjectMaterial.Status.APPROVED,
                    'created_by': user,
                    'document_file': s['file']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created project: {s['title']}"))
                count += 1
            else:
                self.stdout.write(f"Project already exists: {s['title']}")

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} projects.'))
