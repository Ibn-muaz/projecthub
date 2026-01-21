#!/usr/bin/env python
"""
Test script to check the current state of departments and faculty mappings.
Run this to see what needs to be fixed for the "View All" faculty links to work.
"""

import os
import sys
import django

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projecthub.settings')

try:
    django.setup()
    from projects.models import Department
    from projects.constants import FACULTY_DEPARTMENTS
    
    print("🔍 Department Faculty Mapping Analysis")
    print("=" * 60)
    
    # Get all departments
    departments = Department.objects.all()
    print(f"Total departments in database: {departments.count()}")
    
    # Group by faculty
    faculty_departments = {}
    for dept in departments:
        faculty = dept.faculty or 'No Faculty'
        if faculty not in faculty_departments:
            faculty_departments[faculty] = []
        faculty_departments[faculty].append(dept.name)
    
    print(f"\nFaculties found in database:")
    for faculty, depts in faculty_departments.items():
        print(f"  {faculty}: {len(depts)} departments")
    
    # Check for missing faculties
    expected_faculties = set(FACULTY_DEPARTMENTS.keys())
    actual_faculties = set(faculty_departments.keys())
    
    missing_faculties = expected_faculties - actual_faculties
    extra_faculties = actual_faculties - expected_faculties
    
    if missing_faculties:
        print(f"\n❌ Missing faculties (from constants but not in DB):")
        for faculty in missing_faculties:
            print(f"  - {faculty}")
    
    if extra_faculties:
        print(f"\n⚠️  Extra faculties (in DB but not in constants):")
        for faculty in extra_faculties:
            print(f"  - {faculty}")
    
    # Show departments without faculty
    no_faculty = departments.filter(faculty__isnull=True) | departments.filter(faculty='')
    if no_faculty.exists():
        print(f"\n🚨 Departments without faculty assignment:")
        for dept in no_faculty[:10]:  # Show first 10
            print(f"  - {dept.name}")
        if no_faculty.count() > 10:
            print(f"  ... and {no_faculty.count() - 10} more")
    
    # Show sample of what "View All" should find
    print(f"\n📋 Sample: What 'View All' links should find")
    for faculty in expected_faculties:
        db_depts = faculty_departments.get(faculty, [])
        expected_depts = FACULTY_DEPARTMENTS[faculty]
        
        if set(db_depts) != set(expected_depts):
            print(f"\n  {faculty}:")
            print(f"    Expected: {len(expected_depts)} departments")
            print(f"    Found in DB: {len(db_depts)} departments")
            
            missing = set(expected_depts) - set(db_depts)
            extra = set(db_depts) - set(expected_depts)
            
            if missing:
                print(f"    Missing: {', '.join(list(missing)[:3])}")
            if extra:
                print(f"    Extra: {', '.join(list(extra)[:3])}")
    
    print(f"\n✅ Analysis complete!")
    print(f"To fix the 'View All' issue, run: python sync_departments.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure Django is properly configured and the database is accessible.")