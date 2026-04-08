
import os
import django
import sys

# Setup Django environment
sys.path.append('d:/examease/exam')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_data():
    print("--- DEPARTMENTS ---")
    depts = models.Departments.objects.filter(status=1)
    for d in depts:
        print(f"ID: {d.id}, Name: '{d.dept_name}'")

    print("\n--- COURSES ---")
    courses = models.Courses.objects.filter(status=1)
    for c in courses:
        print(f"ID: {c.id}, Name: '{c.course_name}', Dept ID: {c.dept_id}")

    print("\n--- SEMESTERS ---")
    sems = models.Semesters.objects.all().order_by('semester_no')
    for s in sems:
        print(f"ID: {s.id}, Semester: {s.semester_no}, Course ID: {s.course_id}")

if __name__ == '__main__':
    check_data()
