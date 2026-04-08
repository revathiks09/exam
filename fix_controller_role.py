import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import Users

try:
    # Fix Controller
    try:
        user = Users.objects.get(email='controller@examease.com')
        print(f"Current Role: '{user.role}'")
        user.role = 'exam_controller'
        user.save()
        print(f"Updated Role: '{user.role}'")
    except Users.DoesNotExist:
        print("Controller user not found")

    # Check Admin for reference
    try:
        admin = Users.objects.get(email='admin@examease.com')
        print(f"Admin Role: '{admin.role}'")
    except Users.DoesNotExist:
        print("Admin user not found")
        
except Exception as e:
    print(f"Error: {e}")
