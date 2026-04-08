
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_status():
    print("--- Checking Marks Status ---")
    marks = models.Marks.objects.all()
    for m in marks:
        print(f"ID: {m.id}, Student: {m.student.name if m.student else 'None'}, Evaluator: {m.evaluator.name if m.evaluator else 'None'}, Status: '{m.status}'")

if __name__ == "__main__":
    check_status()
