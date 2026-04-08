
import os
import django
import sys
from django.db import connection

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

print("Test: Broken FK with select_related")

# Note: We can't easily insert broken FKs via Django ORM if constraints exist.
# But since managed=False, we can try or use raw SQL.
# Actually, since it's SQLite default, FKs might be disabled or ignored.

try:
    with connection.cursor() as cursor:
        # Create tables if not exist (since managed=False, Django won't create them automatically normally, 
        # but we are using existing DB. Assuming empty for me).
        # I'll try to insert a raw row with invalid FK if table exists.
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses';")
        if not cursor.fetchone():
            print("Creating temp tables for test...")
            cursor.execute("CREATE TABLE courses (id integer primary key, course_name varchar(150), status integer);")
            cursor.execute("CREATE TABLE departments (id integer primary key, dept_name varchar(100), status integer);")
            cursor.execute("CREATE TABLE semesters (id integer primary key, course_id integer, semester_no integer);")
            
        # Clean up
        cursor.execute("DELETE FROM semesters;")
        cursor.execute("DELETE FROM courses;")
        
        # Insert a semester with invalid course_id 999
        print("Inserting semester with course_id=999 (invalid)...")
        cursor.execute("INSERT INTO semesters (course_id, semester_no) VALUES (999, 1);")
        
        # Query via ORM
        print("Querying via ORM...")
        semesters = models.Semesters.objects.select_related('course').all()
        print(f"Count: {semesters.count()}")
        for s in semesters:
            print(f"Semester: {s.semester_no}, Course: {s.course}")

except Exception as e:
    print(f"Error: {e}")
