
from myproject import models
from django.db import connection

def check_data():
    print("--- Checking Evaluators ---")
    evaluators = models.Users.objects.filter(role='evaluator')
    for e in evaluators:
        print(f"ID: {e.id}, Name: {e.name}, Email: {e.email}")

    if not evaluators.exists():
        print("No evaluators found.")
        return

    print("\n--- Checking Mark Assignments ---")
    # Check for any marks assigned to these evaluators
    evaluator_ids = [e.id for e in evaluators]
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM marks WHERE evaluator_id IN %s", [tuple(evaluator_ids)])
        rows = cursor.fetchall()
        if rows:
            print(f"Found {len(rows)} assignments.")
            for row in rows:
                print(row)
        else:
            print("No marks assigned to any evaluator.")

if __name__ == "__main__":
    check_data()
