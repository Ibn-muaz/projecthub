# core/management/commands/sync_departments.py
from django.core.management.base import BaseCommand
from projects.models import Department
from projects.constants import FACULTY_DEPARTMENTS

class Command(BaseCommand):
    help = 'Syncs departments from constants to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting department sync...')
        for faculty, departments in FACULTY_DEPARTMENTS.items():
            for dept_name in departments:
                department, created = Department.objects.get_or_create(
                    name=dept_name,
                    defaults={'faculty': faculty}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created department: {dept_name} in {faculty}'))
                else:
                    # If department exists, ensure faculty is correct
                    if department.faculty != faculty:
                        department.faculty = faculty
                        department.save()
                        self.stdout.write(self.style.WARNING(f'Updated faculty for department: {dept_name} to {faculty}'))

        self.stdout.write(self.style.SUCCESS('Department sync complete.'))
