import os
import django
from django.db import connection

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def create_students_table():
    with connection.cursor() as cursor:
        try:
            print("Creating 'students' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    regno VARCHAR(50),
                    dept_id INT,
                    course_id INT,
                    semester_id INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE SET NULL,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
                    FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("Table 'students' created successfully (or already exists).")
            
            # Verify
            cursor.execute("SHOW TABLES LIKE 'students'")
            if cursor.fetchone():
                print("Verification: Table 'students' exists.")
            else:
                print("Verification: Table 'students' does NOT exist.")
                
        except Exception as e:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_students_table()
