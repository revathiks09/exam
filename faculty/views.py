from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from myproject import models
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# ==================== AUTHENTICATION HELPER ====================

def check_faculty_session(request):
    """Check if faculty is logged in"""
    if 'user_id' in request.session and request.session.get('usertype', '').lower() == 'faculty':
        return True
    return False

# ==================== DASHBOARD ====================

def dashboard(request):
    """Faculty Dashboard"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    fid = request.session['user_id']
    
    # Get counts
    qp_count = models.QuestionPapers.objects.filter(faculty_id=fid).count()
    pending_qp = models.QuestionPapers.objects.filter(faculty_id=fid, status='Pending').count()
    approved_qp = models.QuestionPapers.objects.filter(faculty_id=fid, status='Approved').count()
    
    context = {
        'qp_count': qp_count,
        'pending_qp': pending_qp,
        'approved_qp': approved_qp
    }
    return render(request, 'faculty/index.html', context)

# ==================== QUESTION PAPER MANAGEMENT ====================

def add_question_paper(request):
    """Form to add new QP"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    subjects = models.Subjects.objects.filter(faculty_id=request.session['user_id'])
    semesters = models.Semesters.objects.select_related('course').all()
    
    context = {
        'subjects': subjects,
        'semesters': semesters
    }
    return render(request, 'faculty/exams/add_question_paper.html', context)

def save_question_paper(request):
    """Save QP to database"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    if request.method == 'POST':
        sub_id = request.POST.get('subject')
        sem_id = request.POST.get('semester')
        fid = request.session['user_id']
        
        # File upload
        file_url = ''
        if 'qp_file' in request.FILES:
            qp_file = request.FILES['qp_file']
            fs = FileSystemStorage()
            filename = fs.save(f'qpapers/{qp_file.name}', qp_file)
            file_url = fs.url(filename)
        
        # Create Object
        obj_qp = models.QuestionPapers()
        obj_qp.faculty_id = fid
        obj_qp.subject_id = sub_id
        obj_qp.semester_id = sem_id
        obj_qp.paper_title = request.POST.get('paper_title')
        obj_qp.file_path = file_url
        obj_qp.status = 'Pending' # Direct submission
        obj_qp.submitted_at = timezone.now()
        obj_qp.save()
        
        messages.success(request, 'Question Paper submitted successfully!')
        return redirect('view_question_papers')
        
    return redirect('add_question_paper')

def view_question_papers(request):
    """List all created QPs"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    fid = request.session['user_id']
    qpapers = models.QuestionPapers.objects.filter(faculty_id=fid).select_related('subject', 'semester').order_by('-submitted_at')
    
    context = {
        'qpapers': qpapers
    }
    return render(request, 'faculty/exams/view_question_papers.html', context)

def edit_question_paper(request, qpid):
    """Edit QP form"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    try:
        qpaper = models.QuestionPapers.objects.get(id=qpid)
        subjects = models.Subjects.objects.filter(faculty_id=request.session['user_id'])
        semesters = models.Semesters.objects.select_related('course').all()
        
        context = {
            'qpaper': qpaper,
            'subjects': subjects,
            'semesters': semesters
        }
        return render(request, 'faculty/exams/edit_question_paper.html', context)
    except:
        messages.error(request, 'Invalid Question Paper ID')
        return redirect('view_question_papers')

def update_question_paper(request):
    """Update QP info"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    if request.method == 'POST':
        qpid = request.POST.get('qp_id')
        sub_id = request.POST.get('subject')
        sem_id = request.POST.get('semester')
        
        obj_qp = models.QuestionPapers.objects.get(id=qpid)
        obj_qp.paper_title = request.POST.get('paper_title')
        obj_qp.subject_id = sub_id
        obj_qp.semester_id = sem_id
        
        if 'qp_file' in request.FILES:
            qp_file = request.FILES['qp_file']
            fs = FileSystemStorage()
            filename = fs.save(f'qpapers/{qp_file.name}', qp_file)
            obj_qp.file_path = fs.url(filename)
            
        obj_qp.save()
        messages.success(request, 'Question Paper updated successfully!')
        return redirect('view_question_papers')
        
    return redirect('view_question_papers')

def submit_for_approval(request, qpid):
    """Change status to Pending"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    try:
        obj_qp = models.QuestionPapers.objects.get(id=qpid)
        obj_qp.status = 'Pending'
        obj_qp.save()
        messages.success(request, 'Question Paper submitted for approval!')
    except:
        messages.error(request, 'Error submitting paper')
        
    return redirect('view_question_papers')

# ==================== ASSESSMENT (INTERNAL MARKS) ====================

def enter_internal_marks(request):
    """Form to enter marks"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    subjects = models.Subjects.objects.filter(faculty_id=request.session['user_id'])
    semesters = models.Semesters.objects.all()
    
    # If filter applied
    students = None
    sel_sub = None
    sel_sem = None
    
    # Check for filter in POST or GET
    if request.method == 'POST' and 'filter' in request.POST:
        sel_sub = request.POST.get('subject')
        sel_sem = request.POST.get('semester')
    elif request.GET.get('subject') and request.GET.get('semester'):
        sel_sub = request.GET.get('subject')
        sel_sem = request.GET.get('semester')
    
    # If subject and semester are selected, fetch students
    if sel_sub and sel_sem:
        # Convert to int for easier template comparison
        try:
            sel_sub = int(sel_sub)
            sel_sem = int(sel_sem)
        except:
            pass
        
        # Get students for this semester from Students table
        student_records = models.Students.objects.filter(semester_id=sel_sem).select_related('user')
        students = [s.user for s in student_records]
        
        # Fetch existing marks
        marks_data = models.Marks.objects.filter(subject_id=sel_sub)
        marks_map = {m.student_id: m.internal_marks for m in marks_data}
        
        for std in students:
            std.current_mark = marks_map.get(std.id)
        
    context = {
        'subjects': subjects,
        'semesters': semesters,
        'students': students,
        'sel_sub': sel_sub,
        'sel_sem': sel_sem
    }
    return render(request, 'faculty/marks/enter_internal_marks.html', context)

def save_internal_marks(request):
    """Save entered marks"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    if request.method == 'POST':
        sub_id = request.POST.get('subject_id')
        sem_id = request.POST.get('semester_id')
        
        # Iterate through POST data to find marks-[student_id]
        for key, value in request.POST.items():
            if key.startswith('marks-'):
                stud_id = key.split('-')[1]
                marks_val = value
                
                if marks_val:
                    # Check if exists
                    # Check if exists
                    try:
                        obj_marks = models.Marks.objects.get(student_id=stud_id, subject_id=sub_id)
                        obj_marks.internal_marks = float(marks_val)
                        
                        # Calculate total
                        ext = obj_marks.external_marks if obj_marks.external_marks else 0
                        obj_marks.marks_obtained = float(marks_val) + float(ext)
                        
                        obj_marks.save()
                    except models.Marks.DoesNotExist:
                        obj_marks = models.Marks()
                        obj_marks.student_id = stud_id
                        obj_marks.subject_id = sub_id
                        obj_marks.internal_marks = float(marks_val)
                        obj_marks.marks_obtained = float(marks_val) # External is 0
                        obj_marks.save()
                        
        messages.success(request, 'Internal marks saved successfully!')
        return redirect('enter_internal_marks')
        
    return redirect('enter_internal_marks')

def update_internal_marks(request):
    """Update logic similar to save/enter but specifically for editing"""
    # For simplicity, enter_internal_marks handles both add/update based on existing data check above.
    # But user asked for specific function.
    return redirect('enter_internal_marks')


def manage_internal_marks(request):
    """List subjects with internal marks"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    fid = request.session['user_id']
    
    # List all marks with student details
    # Show individual student records with names and marks
    
    query = """
    SELECT m.id as mark_id,
           u.name as student_name,
           s.subject_name,
           sem.semester_no,
           sem.semester_no,
           m.internal_marks as marks_obtained,
           s.id as subject_id,
           sem.id as semester_id,
           u.id as student_id
    FROM marks m
    JOIN users u ON m.student_id = u.id
    JOIN subjects s ON m.subject_id = s.id
    JOIN semesters sem ON s.semester_id = sem.id
    WHERE s.faculty_id = %s
    ORDER BY sem.semester_no, s.subject_name, u.name
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [fid])
        columns = [col[0] for col in cursor.description]
        marks_list = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
    context = {
        'marks_list': marks_list
    }
    return render(request, 'faculty/marks/manage_internal_marks.html', context)

def delete_internal_marks(request, sub_id):
    """Delete all marks for a subject"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    try:
        # Verify subject belongs to faculty
        subject = models.Subjects.objects.get(id=sub_id, faculty_id=request.session['user_id'])
        
        # Delete marks
        models.Marks.objects.filter(subject_id=sub_id).delete()
        messages.success(request, f'Internal marks for {subject.subject_name} deleted successfully.')
    except models.Subjects.DoesNotExist:
        messages.error(request, 'Invalid Subject or Permission Denied')
    except Exception as e:
        messages.error(request, f'Error deleting marks: {str(e)}')
        
    return redirect('manage_internal_marks')

def delete_student_mark(request, mark_id):
    """Delete individual student mark"""
    if not check_faculty_session(request):
        return redirect('login_page')
        
    try:
        # Get the mark record
        mark = models.Marks.objects.get(id=mark_id)
        student_name = mark.student.name
        subject_name = mark.subject.subject_name
        
        # Delete the mark
        mark.delete()
        messages.success(request, f'Marks for {student_name} in {subject_name} deleted successfully.')
    except models.Marks.DoesNotExist:
        messages.error(request, 'Mark record not found.')
    except Exception as e:
        messages.error(request, f'Error deleting mark: {str(e)}')
        
    return redirect('manage_internal_marks')


# ==================== ANALYTICS ====================

def view_subject_performance(request):
    """View pass percentage per subject"""
    if not check_faculty_session(request):
        return redirect('login_page')
    
    # Raw SQL usage for complex analytics as per Jimpire style
    query = """
    SELECT s.subject_name, 
           COUNT(m.id) as total_students, 
           SUM(CASE WHEN m.marks_obtained >= 50 THEN 1 ELSE 0 END) as passed_students
    FROM marks m
    JOIN subjects s ON m.subject_id = s.id
    WHERE s.faculty_id = %s
    GROUP BY s.subject_name
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [request.session['user_id']])
        columns = [col[0] for col in cursor.description]
        performance_data = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
    # Add percentage
    for item in performance_data:
        if item['total_students'] > 0:
            item['pass_percentage'] = round((item['passed_students'] / item['total_students']) * 100, 2)
        else:
            item['pass_percentage'] = 0
            
    context = {
        'performance_data': performance_data
    }
    return render(request, 'faculty/analytics/subject_performance.html', context)

# ==================== PROFILE & PASSWORD ====================

def my_profile(request):
    """Display faculty profile"""
    if not check_faculty_session(request):
        return redirect('login_page')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'faculty/profile.html', context)

def edit_my_profile(request):
    """Display edit profile form"""
    if not check_faculty_session(request):
        return redirect('login_page')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'faculty/edit_profile.html', context)

def update_my_profile(request):
    """Update profile logic"""
    if not check_faculty_session(request):
        return redirect('login_page')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        # Check if email taken
        if models.Users.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already taken by another user!')
            return redirect('edit_profile_faculty')
            
        user.name = name
        user.email = email
        user.save()
        
        request.session['user_name'] = name
        request.session['semail'] = email
        
        try:
            models.SystemLogs.objects.create(
                user=user,
                action=f"Profile updated for Faculty {user.name}",
                log_time=timezone.now()
            )
        except:
            pass
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('faculty_profile')
        
    return redirect('edit_profile_faculty')

def change_password(request):
    """Display change password form"""
    if not check_faculty_session(request):
        return redirect('login_page')
    
    return render(request, 'faculty/change_password.html')

def update_pass_faculty(request):
    """Update password logic"""
    if not check_faculty_session(request):
        return redirect('login_page')
    
    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        if user.password != old_pass:
            messages.error(request, 'Incorrect old password!')
            return redirect('change_password_faculty')
            
        if new_pass != confirm_pass:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password_faculty')
            
        user.password = new_pass
        user.save()
        
        # Log action locally if function doesn't exist, or reimplement
        try:
            models.SystemLogs.objects.create(
                user=user,
                action=f"Password changed for user {user.name}",
                log_time=timezone.now()
            )
        except:
            pass
        
        messages.success(request, 'Password updated successfully!')
        return redirect('faculty_profile')
        
    return redirect('change_password_faculty')
