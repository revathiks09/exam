
import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

print("Checking Students model fields:")
for field in models.Students._meta.get_fields():
    print(f"- {field.name}: {type(field).__name__}")
    if hasattr(field, 'related_model'):
        print(f"  Related model: {field.related_model}")

print("\nAttempting query:")
try:
    qs = models.Students.objects.select_related('user', 'dept', 'course', 'semester').all()
    print(f"Query: {qs.query}")
    print("Query construction successful")
except Exception as e:
    print(f"Error: {e}")
