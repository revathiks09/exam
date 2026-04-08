
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_students_and_marks():
    print("--- Students ---")
    students = models.Users.objects.filter(role='student')
    for s in students:
        print(f"ID: {s.id}, Name: {s.name}, Status: {s.status}")
    
    print("\n--- Approved Marks ---")
    marks = models.Marks.objects.filter(status__iexact='Approved')
    print(f"Total approved marks: {marks.count()}")
    for m in marks:
        print(f"Student: {m.student.name if m.student else 'None'}, Subject: {m.subject.subject_name if m.subject else 'None'}")
    
    print("\n--- Marks by Status ---")
    from django.db.models import Count
    status_counts = models.Marks.objects.values('status').annotate(count=Count('id'))
    for sc in status_counts:
        print(f"Status: '{sc['status']}' - Count: {sc['count']}")

if __name__ == "__main__":
    check_students_and_marks()
