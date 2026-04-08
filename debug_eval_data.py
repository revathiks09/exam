
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_data():
    print("--- Checking Evaluators ---")
    evaluators = models.Users.objects.filter(role='evaluator')
    for e in evaluators:
        print(f"ID: {e.id}, Name: {e.name}, Email: {e.email}")

    if not evaluators.exists():
        print("No evaluators found.")
    else:
        print("\n--- Checking Mark Assignments ---")
        evaluator_ids = [e.id for e in evaluators]
        if evaluator_ids:
            with connection.cursor() as cursor:
                # Use parameterized query correctly for tuple
                placeholders = ', '.join(['%s'] * len(evaluator_ids))
                query = f"SELECT * FROM marks WHERE evaluator_id IN ({placeholders})"
                cursor.execute(query, evaluator_ids)
                rows = cursor.fetchall()
                if rows:
                    print(f"Found {len(rows)} assignments.")
                    # user_id, student_id, evaluator_id, marks...
                    # Let's see columns
                    desc = [col[0] for col in cursor.description]
                    print(f"Columns: {desc}")
                    for row in rows:
                        print(row)
                else:
                    print("No marks assigned to any evaluator.")

if __name__ == "__main__":
    check_data()
