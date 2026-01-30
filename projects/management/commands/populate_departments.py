
from django.core.management.base import BaseCommand
from projects.models import Department
from projects.constants import FACULTY_DEPARTMENTS

class Command(BaseCommand):
    help = 'Populate departments from constants'

    def handle(self, *args, **options):
        self.stdout.write('Populating departments...')
        count = 0
        for faculty, depts in FACULTY_DEPARTMENTS.items():
            for dept_name in depts:
                dept, created = Department.objects.get_or_create(
                    name=dept_name,
                    defaults={'faculty': faculty}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created: {dept_name} in {faculty}'))
                    count += 1
                else:
                    if dept.faculty != faculty:
                        dept.faculty = faculty
                        dept.save()
                        self.stdout.write(self.style.SUCCESS(f'Updated: {dept_name} to faculty {faculty}'))
                        count += 1

        self.stdout.write(self.style.SUCCESS(f'Done! Populated/Updated {count} departments.'))
        self.stdout.write(self.style.SUCCESS(f'Total departments: {Department.objects.count()}'))
