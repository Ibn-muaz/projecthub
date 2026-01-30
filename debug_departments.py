# Debug view to check departments and faculty
from django.shortcuts import render
from projects.models import Department

def debug_departments(request):
    """Debug view to show current departments and their faculty"""
    departments = Department.objects.all().order_by('faculty', 'name')
    
    # Group departments by faculty
    faculty_departments = {}
    for dept in departments:
        faculty = dept.faculty if dept.faculty else 'No Faculty'
        if faculty not in faculty_departments:
            faculty_departments[faculty] = []
        faculty_departments[faculty].append(dept.name)
    
    # Get unique faculty names, excluding 'No Faculty'
    faculty_names = sorted([f for f in faculty_departments.keys() if f != 'No Faculty'])
    
    context = {
        'departments': departments,
        'faculty_departments': faculty_departments,
        'faculty_names': faculty_names,
        'total_departments': departments.count(),
    }
    
    return render(request, 'core/debug_departments.html', context)