
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_all_statuses():
    print("--- All Marks with Statuses ---")
    marks = models.Marks.objects.all()
    for m in marks:
        print(f"ID: {m.id}, Subject: {m.subject.subject_name if m.subject else 'None'}, Status: '{m.status}' (len={len(m.status) if m.status else 0})")

if __name__ == "__main__":
    check_all_statuses()
