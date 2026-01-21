# projects/management/commands/sync_departments.py
from django.core.management.base import BaseCommand
from projects.models import Department
from projects.constants import FACULTY_DEPARTMENTS


class Command(BaseCommand):
    help = 'Sync departments with proper faculty assignments from constants'

    def handle(self, *args, **options):
        total_created = 0
        total_updated = 0
        
        for faculty_name, department_list in FACULTY_DEPARTMENTS.items():
            for dept_name in department_list:
                # Check if department exists
                department, created = Department.objects.get_or_create(
                    name=dept_name,
                    defaults={
                        'faculty': faculty_name,
                        'is_active': True
                    }
                )
                
                if created:
                    total_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {dept_name} -> {faculty_name}')
                    )
                else:
                    # Update faculty if it doesn't match
                    if department.faculty != faculty_name:
                        old_faculty = department.faculty
                        department.faculty = faculty_name
                        department.save()
                        total_updated += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'Updated: {dept_name} faculty from "{old_faculty}" to "{faculty_name}"'
                            )
                        )
        
        # Show departments without faculty
        departments_without_faculty = Department.objects.filter(
            faculty__isnull=True
        ) | Department.objects.filter(faculty='')
        
        if departments_without_faculty.exists():
            self.stdout.write(
                self.style.ERROR('Departments without faculty:')
            )
            for dept in departments_without_faculty:
                self.stdout.write(f'  - {dept.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sync complete! Created: {total_created}, Updated: {total_updated}'
            )
        )