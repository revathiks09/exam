import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myproject import models

def check_sems():
    sems = models.Semesters.objects.all()
    print("Semesters:")
    for s in sems:
        print(f"ID: {s.id}, No: {s.semester_no}, Course: {s.course_id}")
    
    stud = models.Students.objects.filter(user_id=23).first()
    if stud:
        print(f"\nStudent 23 enrolled in Sem ID: {stud.semester_id}")

if __name__ == "__main__":
    check_sems()
