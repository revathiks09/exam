import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import Users

def create_faculty():
    try:
        # Check if exists
        try:
            user = Users.objects.get(email='faculty@examease.com')
            print("Faculty user already exists.")
            # Ensure role is lowercase 'faculty'
            if user.role != 'faculty':
                user.role = 'faculty'
                user.save()
                print("Updated role to 'faculty'")
        except Users.DoesNotExist:
            user = Users()
            user.name = "Dr. Robert Langdon"
            user.email = "faculty@examease.com"
            user.password = "faculty123"
            user.role = "faculty"
            user.status = 1
            user.created_at = timezone.now()
            user.save()
            print("Created Faculty user: faculty@examease.com / faculty123")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_faculty()
