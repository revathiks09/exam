
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def assign_to_all():
    evaluators = models.Users.objects.filter(role='evaluator')
    student = models.Users.objects.filter(role='student').first()
    subject = models.Subjects.objects.first()
    
    if not evaluators.exists():
        print("No evaluators found!")
        return

    print(f"Assigning Subject '{subject.subject_name}' to {evaluators.count()} Evaluators.")

    for ev in evaluators:
        # Check if already assigned
        exists = models.Marks.objects.filter(
            student=student, 
            subject=subject, 
            evaluator=ev
        ).exists()
        
        if not exists:
            try:
                models.Marks.objects.create(
                    student=student,
                    subject=subject,
                    evaluator=ev,
                    marks_obtained=0,
                    status='Assigned'
                )
                print(f"Assigned to {ev.name} ({ev.email})")
            except Exception as e:
                print(f"Error assigning to {ev.email}: {e}")
        else:
            print(f"Already assigned to {ev.name}")

if __name__ == "__main__":
    assign_to_all()
