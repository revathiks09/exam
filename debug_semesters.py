import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

print("=== Checking Semesters and Courses ===\n")

# Check if semesters exist
semesters = models.Semesters.objects.select_related('course').all()
print(f"Total semesters: {semesters.count()}\n")

for sem in semesters[:10]:  # Show first 10
    course_name = sem.course.course_name if sem.course else "NO COURSE"
    print(f"Semester {sem.semester_no} - Course: {course_name} (course_id: {sem.course_id})")

print("\n=== Checking Courses ===")
courses = models.Courses.objects.all()
print(f"Total courses: {courses.count()}\n")

for course in courses[:5]:
    print(f"Course ID: {course.id} - {course.course_name}")
