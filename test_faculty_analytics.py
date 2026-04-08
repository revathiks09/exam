
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_query():
    print("Testing Faculty Analytics Query...")
    query = """
    SELECT s.subject_name, 
           COUNT(m.id) as total_students, 
           SUM(CASE WHEN m.marks_obtained >= 50 THEN 1 ELSE 0 END) as passed_students
    FROM marks m
    JOIN subjects s ON m.subject_id = s.id
    GROUP BY s.subject_name
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            print("Query executed successfully!")
            print(f"Rows returned: {len(rows)}")
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Query FAILED: {str(e)}")

if __name__ == "__main__":
    test_query()
