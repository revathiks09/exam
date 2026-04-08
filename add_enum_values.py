
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def add_enum_values():
    print("Adding new ENUM values to marks.status...")
    
    with connection.cursor() as cursor:
        # Alter the ENUM to include new values
        cursor.execute("""
            ALTER TABLE marks 
            MODIFY COLUMN status ENUM(
                'ENTERED',
                'MODERATED', 
                'FINALIZED',
                'Assigned',
                'Draft',
                'Approved'
            ) DEFAULT NULL
        """)
        
        print("✓ Successfully added 'Assigned', 'Draft', 'Approved' to status ENUM")
        
        # Verify
        cursor.execute("""
            SELECT COLUMN_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'examease' 
            AND TABLE_NAME = 'marks' 
            AND COLUMN_NAME = 'status'
        """)
        result = cursor.fetchone()
        print(f"\nNew ENUM definition: {result[0]}")

if __name__ == "__main__":
    add_enum_values()
