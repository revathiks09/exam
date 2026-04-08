import os
import django
import sys

# Add project root to path
sys.path.append('d:/examease/exam')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def fix_data():
    try:
        # Get the course
        course = models.Courses.objects.get(id=1)
        print(f"Current: Course {course.course_name} is in Dept ID {course.dept_id}")
        
        if course.course_name == "B.Tech Computer Science" and course.dept_id != 1:
            # Get Computer Science dept
            cs_dept = models.Departments.objects.get(id=1)
            print(f"Updating to Dept: {cs_dept.dept_name} (ID: {cs_dept.id})")
            
            course.dept_id = 1
            course.save()
            print("Successfully updated course department.")
        else:
            print("Course does not match expected problematic state or is already correct.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_data()
