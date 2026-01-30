
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from projects.models import Department
from projects.constants import FACULTY_DEPARTMENTS

def populate_departments():
    print(f"Using DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print("Populating departments...")
    for faculty, depts in FACULTY_DEPARTMENTS.items():
        for dept_name in depts:
            dept, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={'faculty': faculty}
            )
            if created:
                print(f"Created: {dept_name} in {faculty}")
            else:
                if dept.faculty != faculty:
                    dept.faculty = faculty
                    dept.save()
                    print(f"Updated: {dept_name} to faculty {faculty}")

    print(f"Done! Total departments: {Department.objects.count()}")

if __name__ == '__main__':
    populate_departments()
