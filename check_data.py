
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

print("--- EXAMEASE DIAGNOSTIC TOOL ---")

# 1. Check Connection and Basic Counts
print("\n[1] Checking Table Counts:")
try:
    s_count = models.Semesters.objects.count()
    print(f"   Semesters Count (Raw): {s_count}")
    
    c_count = models.Courses.objects.count()
    print(f"   Courses Count: {c_count}")
    
    d_count = models.Departments.objects.count()
    print(f"   Departments Count: {d_count}")
    
except Exception as e:
    print(f"   ERROR reading counts: {e}")

# 2. Check the specific query used in the view
print("\n[2] Testing View Query (select_related):")
try:
    # This is the exact query from views.py
    qs = models.Semesters.objects.select_related('course').all().order_by('semester_no')
    qs_count = qs.count()
    print(f"   Query Count: {qs_count}")
    
    if qs_count == 0 and s_count > 0:
        print("   WARNING: Raw count > 0 but Query count is 0.")
        print("   This suggests 'select_related' is failing to join, possibly due to broken Foreign Keys.")
    elif qs_count > 0:
        print("   Sample Data:")
        for s in qs[:5]:
            c_name = s.course.course_name if s.course else "None"
            print(f"   - Semester: {s.semester_no}, Course ID: {s.course_id}, Course Name: {c_name}")
            
except Exception as e:
    print(f"   ERROR executing view query: {e}")

# 3. Check for Orphaned Semesters
print("\n[3] Checking for Integrity Issues:")
try:
    # Find semesters where course_id is not in Courses table
    # Only if we can iterate
    orphans = 0
    for s in models.Semesters.objects.all():
        if s.course_id:
            if not models.Courses.objects.filter(id=s.course_id).exists():
                print(f"   [CRITICAL] Semester ID {s.id} has course_id {s.course_id} which DOES NOT EXIST in Courses table.")
                orphans += 1
    
    if orphans == 0:
        print("   No orphaned semesters found (Foreign Key integrity looks OK).")
    else:
        print(f"   Found {orphans} orphaned semesters.")

except Exception as e:
    print(f"   Error checking integrity: {e}")

print("\n--- END DIAGNOSTIC ---")
