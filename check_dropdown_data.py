
import os
import django
import sys

# Setup Django environment
sys.path.append('d:/examease/exam')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_data():
    print("Checking Departments...")
    depts = models.Departments.objects.all()
    if not depts:
        print("  WARNING: No Departments found!")
    for d in depts:
        print(f"  ID: {d.id}, Name: {d.dept_name}, Status: {d.status}")

    print("\nChecking Courses...")
    courses = models.Courses.objects.all()
    if not courses:
        print("  WARNING: No Courses found!")
    for c in courses:
        print(f"  ID: {c.id}, Name: {c.course_name}, Dept ID: {c.dept_id}, Status: {c.status}")

    print("\nChecking Semesters...")
    sems = models.Semesters.objects.all()
    if not sems:
        print("  WARNING: No Semesters found!")
    for s in sems:
        print(f"  ID: {s.id}, Semester No: {s.semester_no}, Course ID: {s.course_id}")

    print("\nChecking View Logic Simulation...")
    # Simulate what add_student does
    active_depts = models.Departments.objects.filter(status=1)
    active_courses = models.Courses.objects.filter(status=1)
    all_sems = models.Semesters.objects.select_related('course').all().order_by('semester_no')
    
    print(f"  Active Departments Count: {active_depts.count()}")
    print(f"  Active Courses Count: {active_courses.count()}")
    print(f"  All Semesters Count: {all_sems.count()}")

if __name__ == '__main__':
    check_data()
