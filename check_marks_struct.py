import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

def check_structure():
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE marks")
        rows = cursor.fetchall()
        cols = [row[0] for row in rows]
        with open('marks_structure_clean.txt', 'w') as f:
            f.write(str(cols))

if __name__ == "__main__":
    check_structure()
