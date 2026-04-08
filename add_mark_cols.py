import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

def add_columns():
    with connection.cursor() as cursor:
        # Check if columns exist
        cursor.execute("DESCRIBE marks")
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'internal_marks' not in columns:
            print("Adding internal_marks column...")
            cursor.execute("ALTER TABLE marks ADD COLUMN internal_marks FLOAT DEFAULT 0")
        else:
            print("internal_marks already exists.")
            
        if 'external_marks' not in columns:
            print("Adding external_marks column...")
            cursor.execute("ALTER TABLE marks ADD COLUMN external_marks FLOAT DEFAULT 0")
        else:
            print("external_marks already exists.")

if __name__ == "__main__":
    add_columns()
