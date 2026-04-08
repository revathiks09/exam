import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models
from django.db import connection

def verify_faculty_subjects():
    print("Verifying Faculty Subject Filtering...")

    # 1. Create a Faculty User
    try:
        faculty = models.Users.objects.get(email='test_faculty_verify@test.com')
        print("Found existing test faculty.")
    except models.Users.DoesNotExist:
        faculty = models.Users.objects.create(
            name='Test Faculty Verify',
            email='test_faculty_verify@test.com',
            password='password123',
            role='Faculty',
            status=1,
            created_at=django.utils.timezone.now()
        )
        print("Created test faculty.")

    # 2. Create another Faculty User (to own other subjects)
    try:
        other_faculty = models.Users.objects.get(email='other_faculty@test.com')
        print("Found existing other faculty.")
    except models.Users.DoesNotExist:
        other_faculty = models.Users.objects.create(
            name='Other Faculty',
            email='other_faculty@test.com',
            password='password123',
            role='Faculty',
            status=1,
            created_at=django.utils.timezone.now()
        )

    # 3. Create Semesters, Subjects, and Students if needed
    semester, _ = models.Semesters.objects.get_or_create(semester_no=1)
    
    # Subject assigned to our faculty
    sub_assigned, _ = models.Subjects.objects.get_or_create(
        subject_name='Assigned Subject 101',
        defaults={'semester': semester, 'faculty': faculty}
    )
    if sub_assigned.faculty != faculty:
        sub_assigned.faculty = faculty
        sub_assigned.save()

    # Subject assigned to other faculty
    sub_other, _ = models.Subjects.objects.get_or_create(
        subject_name='Other Subject 102',
        defaults={'semester': semester, 'faculty': other_faculty}
    )
    if sub_other.faculty != other_faculty:
        sub_other.faculty = other_faculty
        sub_other.save()
        
    # Create Student and Marks
    student, _ = models.Students.objects.get_or_create(
        regno='TEST001',
        defaults={
            'course': semester.course, 
            'semester': semester,
            'dept': semester.course.dept if semester.course else None
        }
    )
    # Ensure user exists for student
    if not student.user:
         s_user = models.Users.objects.create(name='Test Student', email='test_stud@test.com', role='Student', created_at=django.utils.timezone.now().date())
         student.user = s_user
         student.save()

    # Create marks for both subjects
    models.Marks.objects.get_or_create(student=student.user, subject=sub_assigned, defaults={'internal_marks': 20, 'marks_obtained': 20})
    models.Marks.objects.get_or_create(student=student.user, subject=sub_other, defaults={'internal_marks': 15, 'marks_obtained': 15})

    print(f"Created/Verified Subject '{sub_assigned.subject_name}' assigned to {faculty.name}")
    print(f"Created/Verified Subject '{sub_other.subject_name}' assigned to {other_faculty.name}")


    # 5. Verify ORM Query Logic
    fid = faculty.id
    filtered_subjects = models.Subjects.objects.filter(faculty_id=fid)
    
    print(f"\n[ORM] Querying subjects for Faculty ID: {fid}")
    print(f"Found {filtered_subjects.count()} subjects.")
    
    found_correct = False
    found_incorrect = False
    
    for sub in filtered_subjects:
        if sub.id == sub_assigned.id: found_correct = True
        if sub.id == sub_other.id: found_incorrect = True
            
    if found_correct and not found_incorrect:
        print("SUCCESS: Only assigned subjects are visible (ORM).")
    else:
        print("FAILURE: Incorrect subjects visible (ORM).")
        
    # 6. Verify SQL Query Logic (manage_internal_marks)
    print(f"\n[SQL] Verify manage_internal_marks query...")
    query = """
    SELECT m.id as mark_id, s.subject_name
    FROM marks m
    JOIN users u ON m.student_id = u.id
    JOIN subjects s ON m.subject_id = s.id
    JOIN semesters sem ON s.semester_id = sem.id
    WHERE s.faculty_id = %s
    ORDER BY sem.semester_no, s.subject_name, u.name
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [fid])
        marks_rows = cursor.fetchall()
        
    print(f"Found {len(marks_rows)} rows in manage_internal_marks query.")
    
    sql_correct = False
    sql_incorrect = False
    
    for row in marks_rows:
        # row[1] is subject_name
        s_name = row[1]
        print(f"- Found Mark for Subject: {s_name}")
        if s_name == sub_assigned.subject_name: sql_correct = True
        if s_name == sub_other.subject_name: sql_incorrect = True
        
    if sql_correct and not sql_incorrect:
        print("SUCCESS: Only assigned subjects are visible (SQL).")
    else:
        print("FAILURE: Incorrect subjects visible (SQL).")

if __name__ == '__main__':
    verify_faculty_subjects()
