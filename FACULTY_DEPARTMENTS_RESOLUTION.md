# "View All" Faculty Departments Issue - Resolution Summary

## Problem Identified
The "View All" links on the landing page for faculty departments were failing to show remaining projects because the faculty field in the Department model didn't match exactly with the faculty names from the FACULTY_DEPARTMENTS constants.

## Root Cause Analysis
1. The landing page template uses faculty names from `FACULTY_DEPARTMENTS` constants
2. The "View All" links pass faculty names as query parameters to the project list view
3. The project list view filters using `department__faculty__iexact=faculty`
4. If the faculty field in Department model doesn't match exactly, no projects are found

## Solutions Implemented

### 1. Debug Tool Created
- **File**: `debug_departments.py` (view function in core/views.py)
- **Template**: `templates/core/debug_departments.html`
- **URL**: `/debug/departments/`
- **Purpose**: Shows current department-faculty mappings and compares with expected constants

### 2. Department Sync Tools Created
- **Standalone Script**: `sync_departments.py` - Can be run directly to populate departments
- **Management Command**: `projects/management/commands/sync_departments.py` - Django management command
- **Function**: Creates/updates departments with proper faculty assignments from constants

### 3. Analysis Script Created
- **File**: `test_departments.py`
- **Purpose**: Analyzes current state and shows what needs fixing
- **Output**: Shows missing faculties, departments without faculty, mismatches

### 4. Documentation Created
- **File**: `FACULTY_DEPARTMENTS_FIX.md`
- **Purpose**: Complete guide for fixing the issue with multiple approaches

## Expected Faculty Names (from constants)
- "Faculty of Administration"
- "Faculty of Arts"
- "Faculty of Education"
- "Faculty of Environmental Science"
- "Faculty of Law"
- "Faculty of Natural and Applied Sciences"
- "Faculty of Social Sciences"
- "Faculty of Medical and Health Sciences"
- "Faculty of Agriculture"

## How to Fix the Issue

### Method 1: Run the Sync Script (Recommended)
```bash
python sync_departments.py
```

### Method 2: Use Django Management Command
```bash
python manage.py sync_departments
```

### Method 3: Manual Fix via Admin
1. Go to `/admin/projects/department/`
2. Update each department's faculty field to match the constants exactly

### Method 4: Use Debug View
1. Navigate to `/debug/departments/`
2. Review the current mappings
3. Use the information to manually fix mismatches

## Verification Steps
After fixing:
1. Go to the landing page
2. Click "View All" under any faculty section
3. The project list should now show projects filtered by that faculty
4. Use the debug view to confirm all mappings are correct

## Files Modified/Added
- `core/views.py` - Added debug_departments view
- `core/urls.py` - Added debug URL pattern
- `templates/core/debug_departments.html` - Debug template
- `sync_departments.py` - Standalone sync script
- `projects/management/commands/sync_departments.py` - Management command
- `test_departments.py` - Analysis script
- `FACULTY_DEPARTMENTS_FIX.md` - Documentation

## Next Steps
1. Run one of the sync methods to populate departments
2. Test the "View All" links on the landing page
3. Verify that faculty filtering works correctly in project list view
4. Check that all expected departments are properly assigned to faculties