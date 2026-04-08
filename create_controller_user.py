import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.models import Users
from django.utils import timezone

# Create exam controller user
try:
    # Check if exam controller already exists
    existing = Users.objects.filter(email='controller@examease.com').first()
    
    if existing:
        print(f"✓ Exam Controller user already exists: {existing.email}")
    else:
        controller = Users()
        controller.name = "Exam Controller"
        controller.email = "controller@examease.com"
        controller.password = "controller123"
        controller.role = "exam_controller"
        controller.status = 1
        controller.created_at = timezone.now()
        controller.save()
        
        print(f"✓ Created Exam Controller user:")
        print(f"  Email: controller@examease.com")
        print(f"  Password: controller123")
        print(f"  Role: exam_controller")
        
except Exception as e:
    print(f"✗ Error creating exam controller: {e}")
