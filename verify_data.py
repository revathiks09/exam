import os
import django
import sys

# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def verify_data():
    with open('verification_output.txt', 'w', encoding='utf-8') as f:
        f.write("--- START VERIFICATION ---\n")
        
        # Check Departments
        depts = models.Departments.objects.filter(status=1)
        f.write(f"Stats: {depts.count()} Active Departments\n")
        for d in depts:
            f.write(f"D: ID={d.id} | Name='{d.dept_name}'\n")

        f.write("\nStats: Checking Courses...\n")
        try:
            courses = models.Courses.objects.select_related('dept').filter(status=1)
            f.write(f"Stats: {courses.count()} Active Courses\n")
            
            for c in courses:
                dept_part = c.dept.dept_name if c.dept else "None"
                f.write(f"C: ID={c.id} | Name='{c.course_name}' | Dept='{dept_part}'\n")
                
        except Exception as e:
            f.write(f"ERROR: {e}\n")

        f.write("--- END VERIFICATION ---\n")

if __name__ == '__main__':
    verify_data()
