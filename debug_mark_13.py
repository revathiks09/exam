import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myproject import models

def check_mark_details():
    try:
        m = models.Marks.objects.get(id=13)
        print(f"Mark ID: {m.id}")
        print(f"Student ID: {m.student_id}")
        print(f"Subject ID: {m.subject_id}")
        print(f"Subject Name: {m.subject.subject_name}")
        print(f"Subject Semester ID: {m.subject.semester_id}")
        print(f"Mark Status: {m.status}")
        
        # Check student enrollment
        student_id = m.student_id
        sem_id = m.subject.semester_id
        
        enrolled = models.Students.objects.filter(user_id=student_id, semester_id=sem_id).exists()
        print(f"Student enrolled in Semester {sem_id}: {enrolled}")
        
        # Check Results existence
        res_exists = models.Results.objects.filter(student_id=student_id, semester_id=sem_id).exists()
        print(f"Result already exists: {res_exists}")
        
    except models.Marks.DoesNotExist:
        print("Mark 13 not found")

if __name__ == "__main__":
    check_mark_details()
