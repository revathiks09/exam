
import os
import django
import sys

# Setup Django environment
sys.path.append('d:/examease/exam')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_semesters():
    print("Checking Semester Counts per Course...")
    courses = models.Courses.objects.all()
    if not courses:
        print("No courses found.")
        return

    has_semesters = False
    for c in courses:
        count = models.Semesters.objects.filter(course=c).count()
        print(f"Course: '{c.course_name}' (ID: {c.id}) -> Semesters: {count}")
        if count > 0:
            has_semesters = True
            # Print first semester details to verify IDs
            first_sem = models.Semesters.objects.filter(course=c).first()
            print(f"   Sample Sem: ID={first_sem.id}, CourseID={first_sem.course_id}")

    if not has_semesters:
        print("\nCRITICAL: No semesters found for any course!")

if __name__ == '__main__':
    check_semesters()
