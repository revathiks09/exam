
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models
from django.utils import timezone

def debug_result_publication():
    print("=== Debugging Result Publication ===\n")
    
    # Check semesters
    print("1. Available Semesters:")
    semesters = models.Semesters.objects.all()
    for sem in semesters:
        print(f"   ID: {sem.id}, Course: {sem.course.course_name if sem.course else 'None'}, Semester: {sem.semester_no}")
    
    if not semesters.exists():
        print("   ERROR: No semesters found!")
        return
    
    semester = semesters.first()
    print(f"\n2. Using Semester: {semester.id} - {semester.course.course_name if semester.course else 'None'} Sem {semester.semester_no}")
    
    # Check enrolled students
    print("\n3. Enrolled Students in this semester:")
    enrolled_students = models.Students.objects.filter(semester=semester).select_related('user')
    print(f"   Count: {enrolled_students.count()}")
    for enrolled in enrolled_students:
        print(f"   - {enrolled.user.name} (ID: {enrolled.user.id})")
    
    if not enrolled_students.exists():
        print("   ERROR: No students enrolled in this semester!")
        return
    
    # Check approved marks
    print("\n4. Checking Approved Marks:")
    for enrolled in enrolled_students:
        student = enrolled.user
        marks = models.Marks.objects.filter(
            student=student,
            subject__semester=semester,
            status__iexact='Approved'
        )
        print(f"\n   Student: {student.name}")
        print(f"   Approved marks count: {marks.count()}")
        
        if marks.exists():
            for m in marks:
                final_mark = m.moderated_marks or m.marks_obtained or 0
                print(f"     - {m.subject.subject_name if m.subject else 'None'}: {final_mark}")
            
            total_marks = sum([m.moderated_marks or m.marks_obtained or 0 for m in marks])
            percentage = (total_marks / (marks.count() * 100)) * 100
            print(f"   Total: {total_marks}, Percentage: {percentage}%")
        else:
            print(f"     No approved marks found!")
    
    # Try to create result manually
    print("\n5. Attempting to create result manually:")
    try:
        student = enrolled_students.first().user
        marks = models.Marks.objects.filter(
            student=student,
            subject__semester=semester,
            status__iexact='Approved'
        )
        
        if marks.exists():
            total_marks = sum([m.moderated_marks or m.marks_obtained or 0 for m in marks])
            percentage = (total_marks / (marks.count() * 100)) * 100
            
            if percentage >= 90:
                grade = 'A+'
            elif percentage >= 80:
                grade = 'A'
            elif percentage >= 70:
                grade = 'B+'
            elif percentage >= 60:
                grade = 'B'
            elif percentage >= 50:
                grade = 'C'
            elif percentage >= 40:
                grade = 'D'
            else:
                grade = 'F'
            
            result_status = 'pass' if percentage >= 40 else 'fail'
            
            result = models.Results()
            result.student = student
            result.semester = semester
            result.total_marks = total_marks
            result.grade = grade
            result.result_status = result_status
            result.published_at = timezone.now()
            result.save()
            
            print(f"   ✓ Result created successfully!")
            print(f"   Student: {student.name}")
            print(f"   Total Marks: {total_marks}")
            print(f"   Grade: {grade}")
            print(f"   Status: {result_status}")
        else:
            print(f"   ERROR: No approved marks to calculate result!")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_result_publication()
