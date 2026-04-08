
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def get_enum_values():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'examease' 
            AND TABLE_NAME = 'marks' 
            AND COLUMN_NAME = 'status'
        """)
        result = cursor.fetchone()
        if result:
            print(f"Status ENUM definition: {result[0]}")

if __name__ == "__main__":
    get_enum_values()
