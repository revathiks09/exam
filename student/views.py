
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from django.http import HttpResponse
from myproject import models

# ==================== AUTHENTICATION ====================

def check_student_session(request):
    """Check if student is logged in"""
    if 'user_id' in request.session and request.session.get('usertype', '').lower() == 'student':
        return True
    return False

def student_login(request):
    """Student Login Page (Redirects to common login)"""
    # Since common login handles all, this might just redirect there or be a specific view if needed.
    # User asked for student_login(), assuming it's the entry point or logic.
    if check_student_session(request):
        return redirect('student_dashboard')
    return redirect('login_page') # Use common login

def student_logout(request):
    """Student Logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    # return redirect('student_login') 
    return redirect('login_page')

# ==================== DASHBOARD & EXAM ACCESS ====================

def dashboard(request):
    """Student Dashboard - Overview"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    
    # Get student details and subjects
    try:
        student = models.Students.objects.select_related('dept', 'semester', 'course').get(user_id=sid)
        my_subjects = models.Subjects.objects.filter(semester_id=student.semester_id).select_related('faculty')
        my_semester = student.semester.semester_no if student.semester else "N/A"
    except models.Students.DoesNotExist:
        student = None
        my_subjects = []
        my_semester = "N/A"
    
    context = {
        'student': student,
        'my_semester': my_semester,
        'my_subjects': my_subjects
    }
    return render(request, 'student/index.html', context)

def view_exam_timetable(request):
    """View Exam Timetable"""
    if not check_student_session(request):
        return redirect('login_page')
    
    # Allow filtering by semester
    semesters = models.Semesters.objects.all()
    timetable = None
    
    if request.method == 'POST':
        sem_id = request.POST.get('semester')
        timetable = models.ExamSchedule.objects.filter(subject__semester_id=sem_id).select_related('subject')
    else:
        # Default to latest HT semester or empty
        sid = request.session['user_id']
        latest_ht = models.HallTickets.objects.filter(student_id=sid).order_by('-issued_date').first()
        if latest_ht:
            timetable = models.ExamSchedule.objects.filter(subject__semester_id=latest_ht.semester_id).select_related('subject')
        
    context = {
        'semesters': semesters,
        'timetable': timetable
    }
    return render(request, 'student/exams/timetable.html', context)

def download_hall_ticket(request):
    """View/Download Hall Ticket"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    hall_tickets = models.HallTickets.objects.filter(student_id=sid).select_related('semester', 'semester__course')
    
    context = {
        'hall_tickets': hall_tickets
    }
    return render(request, 'student/exams/hall_tickets.html', context)

def view_hall_ticket_detail(request, ht_id):
    """View Printable Hall Ticket"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    
    try:
        # Get Hall Ticket
        ht = models.HallTickets.objects.select_related('semester').get(id=ht_id, student_id=sid)
        
        # Get Student Details
        student = models.Students.objects.select_related('user', 'dept').get(user_id=sid)
        
        # Get Exam Schedule for this semester
        exam_schedule = models.ExamSchedule.objects.filter(
            subject__semester_id=ht.semester_id
        ).select_related('subject').order_by('exam_date', 'start_time')
        
        context = {
            'ht': ht,
            'student': student,
            'exam_schedule': exam_schedule
        }
        return render(request, 'student/exams/printable_hall_ticket.html', context)
        
    except (models.HallTickets.DoesNotExist, models.Students.DoesNotExist):
        messages.error(request, 'Hall Ticket not found!')
        return redirect('download_hall_ticket')

def view_seating_arrangement(request):
    """View Seating Arrangement"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    # Join with Subject
    seating = models.SeatingArrangement.objects.filter(student_id=sid).select_related('subject')
    
    context = {
        'seating': seating
    }
    return render(request, 'student/exams/seating.html', context)

# ==================== RESULTS ====================

def view_result(request):
    """View Published Results"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    
    # Get published results
    results = models.Results.objects.filter(student_id=sid).select_related('semester', 'semester__course').order_by('-published_at')
    
    # For each result, get subject-wise marks
    results_with_marks = []
    for result in results:
        # Get marks for this semester
        marks = models.Marks.objects.filter(
            student_id=sid,
            subject__semester=result.semester,
            status__iexact='Approved'
        ).select_related('subject')
        
        results_with_marks.append({
            'result': result,
            'marks': marks
        })
    
    context = {
        'results_with_marks': results_with_marks
    }
    return render(request, 'student/results/view_results.html', context)

def download_grade_sheet(request, rid):
    """Download/Print Grade Sheet for a Result"""
    if not check_student_session(request):
        return redirect('login_page')
        
    try:
        result = models.Results.objects.get(id=rid)
        # Fetch detailed marks for this result's semester/student
        # Assuming Marks table holds subject-wise split.
        marks_details = models.Marks.objects.filter(
            student_id=result.student_id, 
            subject__semester_id=result.semester_id
        ).select_related('subject')
        
        context = {
            'result': result,
            'marks_details': marks_details
        }
        return render(request, 'student/results/grade_sheet.html', context)
    except:
        messages.error(request, 'Result not found')
        return redirect('view_result')

def view_performance_history(request):
    """Visual Performance History"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    
    # Get average marks or grade per semester
    query = """
    SELECT s.semester_no, r.total_marks, r.grade
    FROM results r
    JOIN semesters s ON r.semester_id = s.id
    WHERE r.student_id = %s
    ORDER BY s.semester_no
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [sid])
        columns = [col[0] for col in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    context = {
        'history': history
    }
    return render(request, 'student/results/performance.html', context)

# ==================== RE-EVALUATION ====================

def apply_revaluation(request):
    """Apply for Revaluation"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    
    # Get subjects from Marks/Results that are eligible?
    # For simplicity, allow subjects from last attended sem?
    # Or just list all subjects and let them pick (or filter by result).
    
    subjects = models.Subjects.objects.all() # Better if filtered by student's subjects
    
    if request.method == 'POST':
        sub_id = request.POST.get('subject')
        reason = request.POST.get('reason')
        
        obj = models.RevaluationRequests()
        obj.student_id = sid
        obj.subject_id = sub_id
        obj.reason = reason
        obj.status = 'REQUESTED'
        obj.requested_at = timezone.now()
        obj.save()
        
        messages.success(request, 'Revaluation request submitted successfully!')
        return redirect('track_revaluation_status')
        
    context = {
        'subjects': subjects
    }
    return render(request, 'student/revaluation/apply.html', context)

def track_revaluation_status(request):
    """Track Status of Requests"""
    if not check_student_session(request):
        return redirect('login_page')
        
    sid = request.session['user_id']
    requests = models.RevaluationRequests.objects.filter(student_id=sid).select_related('subject').order_by('-requested_at')
    
    context = {
        'requests': requests
    }
    return render(request, 'student/revaluation/track_status.html', context)

# ==================== PROFILE & PASSWORD ====================

def my_profile(request):
    """Display student profile"""
    if not check_student_session(request):
        return redirect('login_page')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'student/profile.html', context)

def edit_my_profile(request):
    """Display edit profile form"""
    if not check_student_session(request):
        return redirect('login_page')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'student/edit_profile.html', context)

def update_my_profile(request):
    """Update profile logic"""
    if not check_student_session(request):
        return redirect('login_page')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        # Check if email taken
        if models.Users.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already taken by another user!')
            return redirect('edit_profile_student')
            
        user.name = name
        user.email = email
        user.save()
        
        request.session['user_name'] = name
        request.session['semail'] = email
        
        try:
            models.SystemLogs.objects.create(
                user=user,
                action=f"Profile updated for Student {user.name}",
                log_time=timezone.now()
            )
        except:
            pass
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('student_profile')
        
    return redirect('edit_profile_student')

def change_password(request):
    """Display change password form"""
    if not check_student_session(request):
        return redirect('login_page')
    
    return render(request, 'student/change_password.html')

def update_pass_student(request):
    """Update password logic"""
    if not check_student_session(request):
        return redirect('login_page')
    
    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        if user.password != old_pass:
            messages.error(request, 'Incorrect old password!')
            return redirect('change_password_student')
            
        if new_pass != confirm_pass:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password_student')
            
        user.password = new_pass
        user.save()
        
        # Log action locally
        try:
            models.SystemLogs.objects.create(
                user=user,
                action=f"Password changed for user {user.name}",
                log_time=timezone.now()
            )
        except:
            pass
        
        messages.success(request, 'Password updated successfully!')
        return redirect('student_profile')
        
    return redirect('change_password_student')
