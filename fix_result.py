
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def fix_result():
    print("--- Fixing Incorrect Result ---")
    
    # Delete the incorrect result
    deleted = models.Results.objects.all().delete()
    print(f"Deleted {deleted[0]} result(s)")
    
    print("\nNow go to Controller → Approve Results → Select Semester → Approve")
    print("The result will be recalculated with correct marks!")

if __name__ == "__main__":
    fix_result()
