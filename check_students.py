import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

print("=== Checking Students Data ===\n")

# Check total students
total_students = models.Students.objects.count()
print(f"Total students in Students table: {total_students}\n")

if total_students > 0:
    print("First 10 students:")
    students = models.Students.objects.select_related('user', 'semester', 'course', 'dept').all()[:10]
    for s in students:
        print(f"  RegNo: {s.regno} | Name: {s.user.name if s.user else 'NO USER'} | Semester: {s.semester_id} | Course: {s.course_id}")
else:
    print("No students found in Students table!")
    print("\nChecking Users with role='student':")
    user_students = models.Users.objects.filter(role='student').count()
    print(f"Total users with role='student': {user_students}")

print("\n=== Checking Semesters ===")
semesters = models.Semesters.objects.all()[:5]
print(f"Total semesters: {models.Semesters.objects.count()}")
for sem in semesters:
    print(f"  Semester ID: {sem.id} | Semester No: {sem.semester_no}")
