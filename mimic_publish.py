import os
import django
from django.db import connection
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myproject import models

def mimic_publish():
    # Hardcode semester ID 1 based on previous findings
    sem_id = 1
    semester = models.Semesters.objects.get(id=sem_id)
    print(f"Using Semester: {semester.id}")
    
    enrolled_students = models.Students.objects.filter(semester=semester)
    print(f"Enrolled Students: {enrolled_students.count()}")
    
    for enrolled in enrolled_students:
        student = enrolled.user
        print(f"Check Student: {student.id}")
        
        marks = models.Marks.objects.filter(
            student=student, 
            subject__semester=semester,
            status__iexact='Approved'
        )
        print(f" - Marks Status 'Approved' count: {marks.count()}")
        
        # Try raw status check
        marks_all = models.Marks.objects.filter(student=student)
        for m in marks_all:
             print(f"   - Found mark {m.id} status '{m.status}' sem {m.subject.semester_id}")

if __name__ == "__main__":
    mimic_publish()
