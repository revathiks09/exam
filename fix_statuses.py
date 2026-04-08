
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def fix_empty_statuses():
    print("--- Fixing Empty Statuses ---")
    # Update all marks with empty or null status to 'Assigned'
    count = models.Marks.objects.filter(status__isnull=True).update(status='Assigned')
    print(f"Updated {count} NULL statuses to 'Assigned'")
    
    count2 = models.Marks.objects.filter(status='').update(status='Assigned')
    print(f"Updated {count2} empty string statuses to 'Assigned'")
    
    print("\n--- Current Statuses ---")
    marks = models.Marks.objects.all()
    for m in marks:
        print(f"ID: {m.id}, Subject: {m.subject.subject_name if m.subject else 'None'}, Status: '{m.status}'")

if __name__ == "__main__":
    fix_empty_statuses()
