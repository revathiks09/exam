import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject import models

def check_marks_to_file():
    with open('debug_output.txt', 'w') as f:
        try:
            subject = models.Subjects.objects.filter(subject_name__icontains='data structure').first()
            if not subject:
                f.write("Subject 'data structure' not found.\n")
                return
                
            f.write(f"Checking marks for Subject: {subject.subject_name}\n")
            
            marks = models.Marks.objects.filter(subject_id=subject.id)
            
            for m in marks:
                f.write(f"\nStudent: {m.student.name} (ID: {m.student_id})\n")
                f.write(f"  Internal: {m.internal_marks}\n")
                f.write(f"  External: {m.external_marks}\n")
                f.write(f"  Obtained: {m.marks_obtained}\n")
                f.write(f"  Moderated: {m.moderated_marks}\n")
                f.write(f"  Status: {m.status}\n")

        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == '__main__':
    check_marks_to_file()
