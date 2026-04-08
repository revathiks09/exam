
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def assign_work():
    # Fetch resources
    evaluator = models.Users.objects.filter(role='evaluator').first()
    student = models.Users.objects.filter(role='student').first()
    subject = models.Subjects.objects.first()
    
    if not evaluator or not student or not subject:
        print("Missing required data (evaluator, student, or subject).")
        return

    print(f"Assigning Subject '{subject.subject_name}' (ID: {subject.id})")
    print(f"To Evaluator '{evaluator.name}' (ID: {evaluator.id})")
    print(f"For Student '{student.name}' (ID: {student.id})")

    # Create Marks entry
    # Using Django ORM with managed=False works for Data Manipulation if table exists
    try:
        mark = models.Marks(
            student=student,
            subject=subject,
            evaluator=evaluator,
            marks_obtained=0,
            status='Assigned'
        )
        mark.save()
        print(f"Details saved! Mark ID: {mark.id}")
    except Exception as e:
        print(f"Error saving: {e}")

if __name__ == "__main__":
    assign_work()
