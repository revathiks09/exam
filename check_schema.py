
import sqlite3

def check_schema():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    print("--- Table: courses ---")
    cursor.execute("PRAGMA table_info(courses)")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- Table: semesters ---")
    cursor.execute("PRAGMA table_info(semesters)")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Table: students ---")
    cursor.execute("PRAGMA table_info(students)")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == '__main__':
    check_schema()
