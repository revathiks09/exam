
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def check_table_structure():
    with connection.cursor() as cursor:
        cursor.execute("SHOW CREATE TABLE marks")
        result = cursor.fetchone()
        print("Table Structure:")
        print(result[1])

if __name__ == "__main__":
    check_table_structure()
