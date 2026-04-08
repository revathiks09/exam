
import os
import django
import sys

# Setup Django environment
sys.path.append('d:/examease/exam')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def populate_semesters():
    print("Populating Semesters...")
    courses = models.Courses.objects.filter(status=1)
    
    count = 0
    for course in courses:
        # Check if semesters exist
        if not models.Semesters.objects.filter(course=course).exists():
            print(f"Adding 8 semesters for: {course.course_name}")
            for i in range(1, 9):
                models.Semesters.objects.create(
                    course=course,
                    semester_no=i
                )
            count += 1
        else:
            print(f"Skipping {course.course_name} (Semesters already exist)")
            
    print(f"\nDone! Added semesters for {count} courses.")

if __name__ == '__main__':
    populate_semesters()
