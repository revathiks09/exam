
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_marks_calculation():
    print("--- Checking Marks for Result Calculation ---")
    
    # Get the student
    student = models.Users.objects.filter(role='student').first()
    print(f"Student: {student.name} (ID: {student.id})")
    
    # Get their marks
    marks = models.Marks.objects.filter(student=student, status__iexact='Approved')
    print(f"\nApproved Marks Count: {marks.count()}")
    
    for m in marks:
        final_mark = m.moderated_marks or m.marks_obtained or 0
        print(f"Subject: {m.subject.subject_name if m.subject else 'None'}")
        print(f"  Marks Obtained: {m.marks_obtained}")
        print(f"  Moderated Marks: {m.moderated_marks}")
        print(f"  Final Mark Used: {final_mark}")
    
    total = sum([m.moderated_marks or m.marks_obtained or 0 for m in marks])
    print(f"\nTotal Marks: {total}")
    print(f"Subjects Count: {marks.count()}")
    print(f"Percentage: {(total / (marks.count() * 100)) * 100}%")

if __name__ == "__main__":
    check_marks_calculation()
