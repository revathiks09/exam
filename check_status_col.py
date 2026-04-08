
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def check_status_column():
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE marks")
        columns = cursor.fetchall()
        print("Marks Table Columns:")
        for col in columns:
            print(f"{col[0]}: {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
            if col[0] == 'status':
                print(f"\n*** STATUS FIELD: Type={col[1]}, Null={col[2]}, Key={col[3]}, Default={col[4]}, Extra={col[5]}")

if __name__ == "__main__":
    check_status_column()
