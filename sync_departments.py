#!/usr/bin/env python
"""
Standalone script to sync departments with proper faculty assignments.
This script can be run directly to populate/update departments.
"""

import os
import sys
import django

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projecthub.settings')
django.setup()

from projects.models import Department
from projects.constants import FACULTY_DEPARTMENTS


def sync_departments():
    """Sync departments with proper faculty assignments from constants"""
    total_created = 0
    total_updated = 0
    
    print("Starting department sync...")
    print("=" * 50)
    
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
                print(f'✅ CREATED: {dept_name} -> {faculty_name}')
            else:
                # Update faculty if it doesn't match
                if department.faculty != faculty_name:
                    old_faculty = department.faculty
                    department.faculty = faculty_name
                    department.save()
                    total_updated += 1
                    print(f'🔄 UPDATED: {dept_name} faculty from "{old_faculty}" to "{faculty_name}"')
    
    # Show departments without faculty
    departments_without_faculty = Department.objects.filter(
        faculty__isnull=True
    ) | Department.objects.filter(faculty='')
    
    if departments_without_faculty.exists():
        print("\n⚠️  Departments without faculty:")
        for dept in departments_without_faculty:
            print(f'  - {dept.name}')
    
    print("\n" + "=" * 50)
    print(f"✅ Sync complete!")
    print(f"   Created: {total_created}")
    print(f"   Updated: {total_updated}")
    print(f"   Total departments: {Department.objects.count()}")
    
    # Show faculty distribution
    print("\n📊 Faculty distribution:")
    faculty_counts = {}
    for dept in Department.objects.all():
        faculty = dept.faculty or 'No Faculty'
        faculty_counts[faculty] = faculty_counts.get(faculty, 0) + 1
    
    for faculty, count in sorted(faculty_counts.items()):
        print(f"   {faculty}: {count} departments")


if __name__ == '__main__':
    sync_departments()