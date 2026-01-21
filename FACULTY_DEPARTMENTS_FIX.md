# Fix for "View All" Faculty Departments Issue

## Problem
The "View All" links on the landing page for faculty departments are not showing remaining projects because the faculty field in the Department model doesn't match the faculty names from the constants.

## Root Cause
The project list view filters projects using `department__faculty__iexact=faculty`, but the faculty field in the Department model may not match exactly with the faculty names from `FACULTY_DEPARTMENTS` constants.

## Solution

### Option 1: Use the Debug View (Recommended)
1. Navigate to: `http://localhost:8000/debug/departments/`
2. This will show you:
   - Current departments in the database
   - Their faculty assignments
   - Comparison with expected faculty names from constants
   - Missing faculty mappings

### Option 2: Run the Sync Script
1. Run the department sync script:
   ```bash
   python sync_departments.py
   ```

### Option 3: Manual Fix via Django Admin
1. Go to Django admin: `/admin/projects/department/`
2. For each department, ensure the faculty field matches exactly with the faculty names from constants:
   - "Faculty of Administration"
   - "Faculty of Arts"
   - "Faculty of Education"
   - "Faculty of Environmental Science"
   - "Faculty of Law"
   - "Faculty of Natural and Applied Sciences"
   - "Faculty of Social Sciences"
   - "Faculty of Medical and Health Sciences"
   - "Faculty of Agriculture"

### Option 4: Use Django Management Command
1. Run the management command:
   ```bash
   python manage.py sync_departments
   ```

## Verification
After fixing, test the "View All" links on the landing page:
1. Go to the landing page
2. Click "View All" under any faculty section
3. The project list should now show projects filtered by that faculty

## Files Created for Debugging
- `debug_departments.py` - Debug view function
- `templates/core/debug_departments.html` - Debug template
- `sync_departments.py` - Standalone sync script
- `projects/management/commands/sync_departments.py` - Django management command