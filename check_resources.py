
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_resources():
    print("--- Students ---")
    studs = models.Users.objects.filter(role='student')[:5]
    for s in studs:
        print(f"ID: {s.id}, Name: {s.name}")
        
    print("\n--- Subjects ---")
    subs = models.Subjects.objects.all()[:5]
    for s in subs:
        print(f"ID: {s.id}, Name: {s.subject_name}")

if __name__ == "__main__":
    check_resources()
