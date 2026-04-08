
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def manually_approve():
    print("--- Manually Approving Mark ---")
    mark = models.Marks.objects.first()
    if mark:
        print(f"Before: ID={mark.id}, Status='{mark.status}'")
        mark.status = 'Approved'
        mark.save()
        print(f"After save: Status='{mark.status}'")
        
        # Refresh from DB
        mark.refresh_from_db()
        print(f"After refresh: Status='{mark.status}'")
        
        # Check max length
        print(f"\nStatus field max_length: {mark._meta.get_field('status').max_length}")

if __name__ == "__main__":
    manually_approve()
