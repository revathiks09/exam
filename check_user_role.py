import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import Users

try:
    user = Users.objects.get(email='controller@examease.com')
    print(f"User ID: {user.id}")
    print(f"Email: '{user.email}'")
    print(f"Password: '{user.password}'")
    print(f"Role: '{user.role}'")  # Quotes to see whitespace
    print(f"Role Type: {type(user.role)}")
    print(f"Status: {user.status}")
    
    if user.role == 'exam_controller':
        print("MATCH: Role is exactly 'exam_controller'")
    else:
        print("MISMATCH: Role string does not match 'exam_controller'")
        
except Users.DoesNotExist:
    print("User not found!")
