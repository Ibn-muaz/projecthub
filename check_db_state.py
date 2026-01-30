
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from projects.models import Department, ProjectMaterial

print(f"Total Departments: {Department.objects.count()}")
print(f"Total Projects: {ProjectMaterial.objects.count()}")

for dept in Department.objects.all()[:5]:
    print(f"Dept: {dept.name}, Faculty: {dept.faculty}")
