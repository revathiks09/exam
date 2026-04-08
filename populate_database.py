import mysql.connector
from datetime import datetime

# Database connection
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Update if you have a password
        database='examease'
    )
    cursor = conn.cursor()
    print("✅ Connected to database successfully!")
    
    # 1. CREATE ADMIN USER
    print("\n📝 Creating admin user...")
    cursor.execute("""
        INSERT INTO users (name, email, password, role, status, created_at) 
        VALUES ('Admin User', 'admin@examease.com', 'admin123', 'admin', 1, NOW())
    """)
    print("✅ Admin user created!")
    
    # 2. CREATE SAMPLE DEPARTMENTS
    print("\n📝 Creating departments...")
    departments = [
        ('Computer Science', 1),
        ('Electronics & Communication', 1),
        ('Mechanical Engineering', 1),
        ('Civil Engineering', 1),
        ('Information Technology', 1),
        ('Electrical Engineering', 1)
    ]
    cursor.executemany("""
        INSERT INTO departments (dept_name, status) VALUES (%s, %s)
    """, departments)
    print(f"✅ Created {len(departments)} departments!")
    
    # 3. CREATE SAMPLE COURSES
    print("\n📝 Creating courses...")
    courses = [
        (1, 'B.Tech Computer Science', 1),
        (2, 'B.Tech Electronics & Communication', 1),
        (3, 'B.Tech Mechanical Engineering', 1),
        (4, 'B.Tech Civil Engineering', 1),
        (5, 'B.Tech Information Technology', 1),
        (6, 'B.Tech Electrical Engineering', 1),
        (1, 'M.Tech Computer Science', 1),
        (5, 'M.Tech Information Technology', 1)
    ]
    cursor.executemany("""
        INSERT INTO courses (dept_id, course_name, status) VALUES (%s, %s, %s)
    """, courses)
    print(f"✅ Created {len(courses)} courses!")
    
    # 4. CREATE SAMPLE SEMESTERS (for B.Tech CS - course_id = 1)
    print("\n📝 Creating semesters...")
    semesters = [(1, i) for i in range(1, 9)]  # 8 semesters for course 1
    semesters.extend([(2, i) for i in range(1, 9)])  # 8 semesters for course 2
    cursor.executemany("""
        INSERT INTO semesters (course_id, semester_no) VALUES (%s, %s)
    """, semesters)
    print(f"✅ Created {len(semesters)} semesters!")
    
    # 5. CREATE SAMPLE FACULTY USERS
    print("\n📝 Creating faculty users...")
    faculty = [
        ('Dr. John Smith', 'john.smith@examease.com', 'faculty123', 'faculty', 1),
        ('Dr. Sarah Johnson', 'sarah.johnson@examease.com', 'faculty123', 'faculty', 1),
        ('Prof. Michael Brown', 'michael.brown@examease.com', 'faculty123', 'faculty', 1),
        ('Dr. Emily Davis', 'emily.davis@examease.com', 'faculty123', 'faculty', 1),
        ('Prof. David Wilson', 'david.wilson@examease.com', 'faculty123', 'faculty', 1)
    ]
    for f in faculty:
        cursor.execute("""
            INSERT INTO users (name, email, password, role, status, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, f)
    print(f"✅ Created {len(faculty)} faculty users!")
    
    # 6. CREATE SAMPLE STUDENT USERS
    print("\n📝 Creating student users...")
    students = [
        ('Alice Williams', 'alice.williams@student.com', 'student123', 'student', 1),
        ('Bob Davis', 'bob.davis@student.com', 'student123', 'student', 1),
        ('Charlie Wilson', 'charlie.wilson@student.com', 'student123', 'student', 1),
        ('Diana Martinez', 'diana.martinez@student.com', 'student123', 'student', 1),
        ('Eve Anderson', 'eve.anderson@student.com', 'student123', 'student', 1),
        ('Frank Thomas', 'frank.thomas@student.com', 'student123', 'student', 1),
        ('Grace Taylor', 'grace.taylor@student.com', 'student123', 'student', 1),
        ('Henry Moore', 'henry.moore@student.com', 'student123', 'student', 1),
        ('Iris Jackson', 'iris.jackson@student.com', 'student123', 'student', 1),
        ('Jack White', 'jack.white@student.com', 'student123', 'student', 1)
    ]
    for s in students:
        cursor.execute("""
            INSERT INTO users (name, email, password, role, status, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, s)
    print(f"✅ Created {len(students)} student users!")
    
    # 7. CREATE SAMPLE EVALUATOR USERS
    print("\n📝 Creating evaluator users...")
    evaluators = [
        ('Dr. Robert Taylor', 'robert.taylor@examease.com', 'eval123', 'evaluator', 1),
        ('Dr. Linda Thomas', 'linda.thomas@examease.com', 'eval123', 'evaluator', 1),
        ('Dr. James Harris', 'james.harris@examease.com', 'eval123', 'evaluator', 1)
    ]
    for e in evaluators:
        cursor.execute("""
            INSERT INTO users (name, email, password, role, status, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, e)
    print(f"✅ Created {len(evaluators)} evaluator users!")
    
    # Commit all changes
    conn.commit()
    
    # Verification
    print("\n" + "="*50)
    print("📊 VERIFICATION - Data Summary")
    print("="*50)
    
    cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
    for row in cursor.fetchall():
        print(f"  {row[0].capitalize()}: {row[1]} users")
    
    cursor.execute("SELECT COUNT(*) FROM departments")
    print(f"  Departments: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM courses")
    print(f"  Courses: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM semesters")
    print(f"  Semesters: {cursor.fetchone()[0]}")
    
    print("\n" + "="*50)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("="*50)
    print("\n🔐 LOGIN CREDENTIALS:")
    print("  Admin:")
    print("    Email: admin@examease.com")
    print("    Password: admin123")
    print("\n  Faculty:")
    print("    Email: john.smith@examease.com")
    print("    Password: faculty123")
    print("\n  Student:")
    print("    Email: alice.williams@student.com")
    print("    Password: student123")
    print("\n  Evaluator:")
    print("    Email: robert.taylor@examease.com")
    print("    Password: eval123")
    print("="*50)
    
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
    if 'Duplicate entry' in str(err):
        print("\n⚠️  Data already exists in the database!")
        print("   If you want to reset, please clear the tables first.")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("\n✅ Database connection closed.")
