from django.shortcuts import render, redirect
from django.contrib import messages
from myproject import models, views as common_views
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import random

# ==================== AUTHENTICATION ====================

def controller_login(request):
    """Display exam controller login page"""
    return render(request, 'controller/login.html')

def check_controller_login(request):
    """Verify exam controller credentials and create session"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = models.Users.objects.get(email=email, password=password, role='exam_controller')
            
            if user.status == 1:  # Active user
                # Create session
                request.session['user_id'] = user.id
                request.session['semail'] = user.email
                request.session['user_name'] = user.name
                request.session['usertype'] = user.role
                
                # Save session explicitly
                request.session.save()
                
                # Log login session
                models.LoginSessions.objects.create(
                    user=user,
                    login_time=timezone.now(),
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Log system action
                log_system_action(user, f"Exam Controller {user.name} logged in")
                
                messages.success(request, f'Welcome back, {user.name}!')
                return redirect('controller_dashboard')
            else:
                messages.error(request, 'Your account is deactivated. Please contact support.')
                return redirect('controller_login')
                
        except models.Users.DoesNotExist:
            messages.error(request, 'Invalid email or password!')
            return redirect('controller_login')
    
    return redirect('controller_login')

def controller_logout(request):
    """Logout exam controller and clear session"""
    if 'user_id' in request.session:
        try:
            user = models.Users.objects.get(id=request.session['user_id'])
            
            # Update logout time in login session
            last_session = models.LoginSessions.objects.filter(
                user=user, 
                logout_time__isnull=True
            ).order_by('-login_time').first()
            
            if last_session:
                last_session.logout_time = timezone.now()
                last_session.save()
            
            # Log system action
            log_system_action(user, f"Exam Controller {user.name} logged out")
            
        except:
            pass
    
    # Clear session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

# ==================== DASHBOARD ====================

def controller_dashboard(request):
    """Exam controller dashboard with statistics"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Get statistics
    total_papers = models.QuestionPapers.objects.count()
    pending_papers = models.QuestionPapers.objects.filter(status='pending').count()
    approved_papers = models.QuestionPapers.objects.filter(status='approved').count()
    rejected_papers = models.QuestionPapers.objects.filter(status='rejected').count()
    
    total_exams = models.ExamSchedule.objects.count()
    upcoming_exams = models.ExamSchedule.objects.filter(exam_date__gte=timezone.now().date()).count()
    
    total_students = models.Users.objects.filter(role='student').count()
    hall_tickets_generated = models.HallTickets.objects.count()
    
    seating_arranged = models.SeatingArrangement.objects.count()
    
    # Mark entry statistics
    total_marks = models.Marks.objects.count()
    # "Pending" includes Assigned, Draft, and Empty
    pending_marks = models.Marks.objects.filter(Q(status__iexact='Assigned') | Q(status__iexact='Draft') | Q(status='') | Q(status__isnull=True) | Q(status__iexact='ENTERED')).count()
    approved_marks = models.Marks.objects.filter(status__iexact='Approved') | models.Marks.objects.filter(status__iexact='MODERATED')
    approved_marks = approved_marks.count()
    
    # Recent question papers
    recent_papers = models.QuestionPapers.objects.select_related('subject', 'faculty').order_by('-submitted_at')[:5]
    
    # Recent exam schedules
    recent_exams = models.ExamSchedule.objects.select_related('subject').order_by('-exam_date')[:5]
    
    context = {
        'total_papers': total_papers,
        'pending_papers': pending_papers,
        'approved_papers': approved_papers,
        'rejected_papers': rejected_papers,
        'total_exams': total_exams,
        'upcoming_exams': upcoming_exams,
        'total_students': total_students,
        'hall_tickets_generated': hall_tickets_generated,
        'seating_arranged': seating_arranged,
        'total_marks': total_marks,
        'pending_marks': pending_marks,
        'approved_marks': approved_marks,
        'recent_papers': recent_papers,
        'recent_exams': recent_exams,
    }
    
    return render(request, 'controller/index.html', context)

# ==================== QUESTION PAPER CONTROL ====================

def view_submitted_papers(request):
    """List all submitted question papers"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Get filter parameter
    status_filter = request.GET.get('status', 'all')
    
    # Query papers with joins
    if status_filter == 'all':
        papers = models.QuestionPapers.objects.select_related('subject', 'faculty').order_by('-submitted_at')
    else:
        papers = models.QuestionPapers.objects.select_related('subject', 'faculty').filter(status=status_filter).order_by('-submitted_at')
    
    context = {
        'papers': papers,
        'status_filter': status_filter
    }
    return render(request, 'controller/question_papers/submitted_papers.html', context)

def approve_question_paper(request, paper_id):
    """Approve a question paper"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    paper = models.QuestionPapers.objects.get(id=paper_id)
    paper.status = 'approved'
    paper.save()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Approved question paper: {paper.paper_title}")
    
    messages.success(request, f'Question paper "{paper.paper_title}" approved successfully!')
    return redirect('view_submitted_papers')

def reject_question_paper(request, paper_id):
    """Reject a question paper"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        paper = models.QuestionPapers.objects.get(id=paper_id)
        paper.status = 'rejected'
        paper.save()
        
        # Log action with reason
        reason = request.POST.get('reason', 'No reason provided')
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Rejected question paper: {paper.paper_title} - Reason: {reason}")
        
        messages.warning(request, f'Question paper "{paper.paper_title}" rejected!')
        return redirect('view_submitted_papers')
    
    # Show rejection form
    paper = models.QuestionPapers.objects.get(id=paper_id)
    context = {'paper': paper}
    return render(request, 'controller/question_papers/reject_paper.html', context)

# ==================== EXAM MANAGEMENT ====================

def create_exam_schedule(request):
    """Display form to create exam schedule"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    subjects = models.Subjects.objects.select_related('semester').all()
    context = {'subjects': subjects}
    return render(request, 'controller/exams/create_schedule.html', context)

def save_exam_schedule(request):
    """Save new exam schedule"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        exam_date = request.POST.get('exam_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        subject = models.Subjects.objects.get(id=subject_id)
        
        # Create exam schedule
        schedule = models.ExamSchedule()
        schedule.subject = subject
        schedule.exam_date = exam_date
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Created exam schedule for {subject.subject_name} on {exam_date}")
        
        messages.success(request, f'Exam schedule created for {subject.subject_name}!')
        return redirect('exam_timetable')
    
    return redirect('create_exam_schedule')

def edit_exam_schedule(request, schedule_id):
    """Display form to edit exam schedule"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    schedule = models.ExamSchedule.objects.get(id=schedule_id)
    subjects = models.Subjects.objects.select_related('semester').all()
    
    context = {
        'schedule': schedule,
        'subjects': subjects
    }
    return render(request, 'controller/exams/edit_schedule.html', context)

def update_exam_schedule(request):
    """Update existing exam schedule"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        subject_id = request.POST.get('subject_id')
        exam_date = request.POST.get('exam_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        schedule = models.ExamSchedule.objects.get(id=schedule_id)
        subject = models.Subjects.objects.get(id=subject_id)
        
        # Update fields
        schedule.subject = subject
        schedule.exam_date = exam_date
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Updated exam schedule for {subject.subject_name}")
        
        messages.success(request, f'Exam schedule updated for {subject.subject_name}!')
        return redirect('exam_timetable')
        
    return redirect('exam_timetable')

def delete_exam_schedule(request, schedule_id):
    """Delete exam schedule"""
    if not check_controller_session(request):
        return redirect('controller_login')
        
    try:
        schedule = models.ExamSchedule.objects.get(id=schedule_id)
        subject_name = schedule.subject.subject_name
        schedule.delete()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Deleted exam schedule for {subject_name}")
        
        messages.success(request, 'Exam schedule deleted successfully!')
    except Exception as e:
        messages.error(request, 'Error deleting schedule!')
        
    return redirect('exam_timetable')

def publish_exam_timetable(request):
    """View and publish exam timetable"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Get all exam schedules
    schedules = models.ExamSchedule.objects.select_related('subject').order_by('exam_date', 'start_time')
    
    context = {'schedules': schedules}
    return render(request, 'controller/exams/exam_timetable.html', context)

def generate_seating_arrangement(request):
    """Auto-generate seating arrangements"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        subject = models.Subjects.objects.get(id=subject_id)
        
        # Get all students for this semester
        semester = subject.semester
        students = models.Users.objects.filter(role='student', status=1)
        
        # Clear existing seating for this subject
        models.SeatingArrangement.objects.filter(subject=subject).delete()
        
        # Generate seating arrangement
        hall_no = 1
        seat_no = 1
        max_seats_per_hall = 30
        
        for student in students:
            seating = models.SeatingArrangement()
            seating.student = student
            seating.subject = subject
            seating.hall_no = f"Hall-{hall_no}"
            seating.seat_no = f"S-{seat_no}"
            seating.save()
            
            seat_no += 1
            if seat_no > max_seats_per_hall:
                seat_no = 1
                hall_no += 1
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Generated seating arrangement for {subject.subject_name}")
        
        messages.success(request, f'Seating arrangement generated for {subject.subject_name}!')
        return redirect('controller_view_seating')
    
    # Show form
    subjects = models.Subjects.objects.select_related('semester').all()
    context = {'subjects': subjects}
    return render(request, 'controller/exams/generate_seating.html', context)

def view_seating_arrangement(request):
    """View seating arrangements"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Get filter parameter
    subject_id = request.GET.get('subject_id', None)
    
    if subject_id:
        seating = models.SeatingArrangement.objects.select_related('student', 'subject').filter(subject_id=subject_id).order_by('hall_no', 'seat_no')
    else:
        seating = models.SeatingArrangement.objects.select_related('student', 'subject').order_by('subject', 'hall_no', 'seat_no')
    
    subjects = models.Subjects.objects.all()
    
    context = {
        'seating': seating,
        'subjects': subjects,
        'selected_subject': subject_id
    }
    return render(request, 'controller/exams/seating_arrangement.html', context)

def generate_hall_ticket(request):
    """Generate hall tickets for students"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        semester_id = request.POST.get('semester_id')
        semester = models.Semesters.objects.get(id=semester_id)
        
        # Get all students
        students = models.Users.objects.filter(role='student', status=1)
        
        # Generate hall tickets
        count = 0
        for student in students:
            # Check if hall ticket already exists
            existing = models.HallTickets.objects.filter(student=student, semester=semester).first()
            if not existing:
                hall_ticket = models.HallTickets()
                hall_ticket.student = student
                hall_ticket.semester = semester
                hall_ticket.issued_date = timezone.now().date()
                hall_ticket.save()
                count += 1
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Generated {count} hall tickets for semester {semester.semester_no}")
        
        messages.success(request, f'{count} hall tickets generated successfully!')
        return redirect('view_hall_tickets')
    
    # Show form
    semesters = models.Semesters.objects.select_related('course').all()
    context = {'semesters': semesters}
    return render(request, 'controller/exams/generate_hall_ticket.html', context)

def view_hall_tickets(request):
    """View generated hall tickets"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    hall_tickets = models.HallTickets.objects.select_related('student', 'semester').order_by('-issued_date')
    
    context = {'hall_tickets': hall_tickets}
    return render(request, 'controller/exams/hall_tickets.html', context)


# ==================== EVALUATOR ASSIGNMENT ====================

def assign_evaluator(request):
    """Assign scripts to evaluators"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        evaluator_id = request.POST.get('evaluator_id')
        
        try:
            subject = models.Subjects.objects.get(id=subject_id)
            evaluator = models.Users.objects.get(id=evaluator_id, role='evaluator')
            
            # Get students for this subject's semester
            students = models.Users.objects.filter(
                role='student',
                status=1
                # In a real scenario, we might want to filter by students enrolled in the course/semester explicitly
                # checking student.semester == subject.semester
            )
            
            # We need to filter students who belong to the semester of the subject
            # Since Users model doesn't have semester directly visible here (it's in Students table mostly?)
            # Wait, models.Students has 'user', 'semester'. models.Users is just auth.
            # But let's check models.py again.
            # models.Students has user_id, semester_id.
            
            # Re-fetching correct students via Students model
            enrolled_students = models.Students.objects.filter(semester=subject.semester)
            
            count = 0
            for enrolled in enrolled_students:
                student_user = enrolled.user
                
                # Check if entry exists, if so update it, else create it
                try:
                    mark_entry = models.Marks.objects.filter(
                        student=student_user,
                        subject=subject
                    ).first()
                    
                    if mark_entry:
                        # Update existing entry
                        mark_entry.evaluator = evaluator
                        if not mark_entry.status:
                             mark_entry.status = 'Assigned'
                        mark_entry.save()
                        count += 1
                    else:
                        # Create new assignment
                        models.Marks.objects.create(
                            student=student_user,
                            subject=subject,
                            evaluator=evaluator,
                            marks_obtained=0,
                            status='Assigned'
                        )
                        count += 1
                except Exception as inner_e:
                    print(f"Error for student {student_user.id}: {inner_e}")
                    continue
            
            # Log action
            current_user = models.Users.objects.get(id=request.session['user_id'])
            log_system_action(current_user, f"Assigned {count} scripts of {subject.subject_name} to {evaluator.name}")
            
            messages.success(request, f'Successfully assigned {count} scripts to {evaluator.name}!')
            
        except Exception as e:
            messages.error(request, f'Error assigning scripts: {str(e)}')
            
        return redirect('assign_evaluator')
        
    # GET request - Show form
    subjects = models.Subjects.objects.select_related('semester', 'semester__course').all()
    evaluators = models.Users.objects.filter(role='evaluator', status=1)
    
    context = {
        'subjects': subjects,
        'evaluators': evaluators
    }
    return render(request, 'controller/exams/assign_evaluator.html', context)

def view_assignments(request):
    """View all evaluator assignments"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Aggregate marks to show count of scripts per subject per evaluator
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.id as subject_id,
                s.subject_name,
                e.id as evaluator_id,
                e.name as evaluator_name,
                COUNT(m.id) as script_count,
                MAX(m.status) as status_example
            FROM marks m
            JOIN subjects s ON m.subject_id = s.id
            JOIN users e ON m.evaluator_id = e.id
            GROUP BY s.id, s.subject_name, e.id, e.name
            ORDER BY s.subject_name
        """)
        columns = [col[0] for col in cursor.description]
        assignments = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    context = {'assignments': assignments}
    return render(request, 'controller/exams/view_assignments.html', context)

def edit_assignment(request, subject_id, evaluator_id):
    """Re-assign scripts from one evaluator to another"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    current_evaluator = models.Users.objects.get(id=evaluator_id)
    subject = models.Subjects.objects.get(id=subject_id)
    
    if request.method == 'POST':
        new_evaluator_id = request.POST.get('new_evaluator_id')
        new_evaluator = models.Users.objects.get(id=new_evaluator_id)
        
        # Update records
        updated_count = models.Marks.objects.filter(
            subject_id=subject_id, 
            evaluator_id=evaluator_id
        ).update(evaluator=new_evaluator)
        
        # Log
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Re-assigned {updated_count} scripts of {subject.subject_name} from {current_evaluator.name} to {new_evaluator.name}")
        
        messages.success(request, f'Re-assigned {updated_count} scripts successfully!')
        return redirect('view_assignments')
        
    # Show form
    evaluators = models.Users.objects.filter(role='evaluator', status=1).exclude(id=evaluator_id)
    
    context = {
        'subject': subject,
        'current_evaluator': current_evaluator,
        'evaluators': evaluators
    }
    return render(request, 'controller/exams/edit_assignment.html', context)

# ==================== MARK APPROVAL ====================

def view_pending_marks(request):
    """View marks pending approval"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Get all finalized marks
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                m.id,
                u.name as student_name,
                s.subject_name,
                e.name as evaluator_name,
                m.marks_obtained,
                m.moderated_marks,
                m.status
            FROM marks m
            JOIN users u ON m.student_id = u.id
            JOIN subjects s ON m.subject_id = s.id
            JOIN users e ON m.evaluator_id = e.id
            WHERE UPPER(m.status) = 'FINALIZED'
            ORDER BY s.subject_name, u.name
        """)
        columns = [col[0] for col in cursor.description]
        pending_marks = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {'pending_marks': pending_marks}
    return render(request, 'controller/marks/pending_marks.html', context)

def approve_marks(request):
    """Approve finalized marks"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        mark_ids = request.POST.getlist('mark_ids')
        
        if mark_ids:
            count = models.Marks.objects.filter(
                id__in=mark_ids,
                status__iexact='FINALIZED'
            ).update(status='Approved')
            
            # Log action
            current_user = models.Users.objects.get(id=request.session['user_id'])
            log_system_action(current_user, f"Approved {count} marks")
            
            messages.success(request, f'Successfully approved {count} marks!')
        else:
            messages.warning(request, 'No marks selected for approval')
    
    return redirect('view_pending_marks')

def reject_marks(request, mark_id):
    """Reject marks back to evaluator"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    try:
        mark = models.Marks.objects.get(id=mark_id)
        mark.status = 'Draft'
        mark.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Rejected marks for student ID {mark.student_id}")
        
        messages.warning(request, 'Marks rejected and sent back to evaluator')
    except models.Marks.DoesNotExist:
        messages.error(request, 'Invalid mark ID')
    
    return redirect('view_pending_marks')

# ==================== RESULT SUPERVISION ====================

def monitor_mark_entry(request):
    """Monitor mark entry status across all subjects"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    # Get mark entry statistics by subject
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.id,
                s.subject_name,
                COUNT(m.id) as total_entries,
                SUM(CASE WHEN m.status IS NULL OR m.status = '' OR UPPER(m.status) = 'ASSIGNED' OR UPPER(m.status) = 'DRAFT' THEN 1 ELSE 0 END) as pending_count,
                SUM(CASE WHEN UPPER(m.status) = 'APPROVED' THEN 1 ELSE 0 END) as approved_count,
                SUM(CASE WHEN UPPER(m.status) = 'FINALIZED' THEN 1 ELSE 0 END) as finalized_count
            FROM subjects s
            LEFT JOIN marks m ON s.id = m.subject_id
            GROUP BY s.id, s.subject_name
            ORDER BY s.subject_name
        """)
        
        columns = [col[0] for col in cursor.description]
        mark_stats = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {'mark_stats': mark_stats}
    return render(request, 'controller/results/monitor_marks.html', context)

def approve_final_results(request):
    """Approve and publish final results"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        semester_id = request.POST.get('semester_id')
        semester = models.Semesters.objects.get(id=semester_id)
        
        # Get students who have marks in this semester
        # Use Students table to get proper semester enrollment
        enrolled_students = models.Students.objects.filter(semester=semester).select_related('user')
        
        # Calculate and publish results
        count = 0
        skipped_count = 0
        no_marks_count = 0
        
        print(f"DEBUG: Processing Results for Semester {semester.id}")
        print(f"DEBUG: Found {enrolled_students.count()} enrolled students")
        
        for enrolled in enrolled_students:
            student = enrolled.user
            
            # Check if result already exists
            existing = models.Results.objects.filter(student=student, semester=semester).first()
            if not existing:
                # Calculate total marks for this student in this semester
                marks = models.Marks.objects.filter(
                    student=student,
                    subject__semester=semester,
                    status__iexact='Approved'
                )
                
                if marks.exists():
                    total_marks = sum([m.moderated_marks if m.moderated_marks is not None else (m.marks_obtained if m.marks_obtained is not None else 0) for m in marks])
                    
                    # Calculate grade
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
                    
                    result_status = 'PASS' if percentage >= 40 else 'FAIL'
                    
                    # Create result
                    result = models.Results()
                    result.student = student
                    result.semester = semester
                    result.total_marks = total_marks
                    result.grade = grade
                    result.result_status = result_status
                    result.published_at = timezone.now()
                    result.save()
                    count += 1
                else:
                    no_marks_count += 1
                    print(f"DEBUG: No approved marks for student {student.id}")
            else:
                skipped_count += 1
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Approved results for Sem {semester.semester_no}: {count} published, {skipped_count} skipped, {no_marks_count} incomplete")
        
        if count > 0:
            messages.success(request, f'{count} results approved and published successfully!')
        else:
            if skipped_count > 0:
                 messages.warning(request, f'No new results published. {skipped_count} students already have results.')
            elif no_marks_count > 0:
                 messages.error(request, f'No results published. {no_marks_count} students have no approved marks found.')
            else:
                 messages.warning(request, 'No students found for this semester.')
        return redirect('view_results')
    
    # Show form
    semesters = models.Semesters.objects.select_related('course').all()
    context = {'semesters': semesters}
    return render(request, 'controller/results/approve_results.html', context)

def view_results(request):
    """View published results"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    results = models.Results.objects.select_related('student', 'semester').order_by('-published_at')[:50]
    
    context = {'results': results}
    return render(request, 'controller/results/view_results.html', context)

# ==================== HELPER FUNCTIONS ====================


# ==================== REVALUATION ====================

def view_revaluation_requests(request):
    """View all revaluation requests"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    requests = models.RevaluationRequests.objects.select_related('student', 'subject').order_by('-requested_at')
    
    # Attach mark details manually since we can't easily join unrelated models in simple ORM without related_name setup or complex Prefetch
    for req in requests:
        try:
            m = models.Marks.objects.get(student=req.student, subject=req.subject)
            req.mark_details = m
        except models.Marks.DoesNotExist:
            req.mark_details = None
            
    context = {'requests': requests}
    return render(request, 'controller/revaluation/requests.html', context)

def process_revaluation(request):
    """Process a revaluation request"""
    if not check_controller_session(request):
        return redirect('controller_login')
        
    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        action = request.POST.get('action')
        new_marks = request.POST.get('new_marks')
        
        try:
            req = models.RevaluationRequests.objects.get(id=req_id)
            
            if action == 'Update Marks' and new_marks:
                print(f"DEBUG: Processing Update for Req {req.id}. New External Marks: {new_marks}")
                
                # Update Marks
                mark_entry = models.Marks.objects.get(
                    student=req.student,
                    subject=req.subject
                )
                
                print(f"DEBUG: Found Mark Entry {mark_entry.id}. Old External: {mark_entry.external_marks}")
                
                new_ext = float(new_marks)
                internal = mark_entry.internal_marks if mark_entry.internal_marks is not None else 0
                
                # Calculate New Total
                new_total = internal + new_ext
                
                # Update all fields
                mark_entry.external_marks = new_ext
                mark_entry.moderated_marks = new_total
                mark_entry.marks_obtained = new_total
                mark_entry.status = 'Approved' 
                mark_entry.save()
                
                print(f"DEBUG: Mark updated. New External: {new_ext}, Internal: {internal}, New Total: {new_total}")
                
                req.status = 'COMPLETED'
                req.save()
                
                # Recalculate Result if it exists
                # Find the semester
                semester = req.subject.semester
                
                # Find the result for this student and semester
                result = models.Results.objects.filter(
                    student=req.student,
                    semester=semester
                ).first()
                
                if result:
                    # Recalculate total
                    marks = models.Marks.objects.filter(
                        student=req.student,
                        subject__semester=semester,
                        status__iexact='Approved'
                    )
                    
                    total_marks = sum([m.moderated_marks if m.moderated_marks is not None else (m.marks_obtained if m.marks_obtained is not None else 0) for m in marks])
                    
                    # Update Result
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
                    
                    result_status = 'PASS' if percentage >= 40 else 'FAIL'
                    
                    result.total_marks = total_marks
                    result.grade = grade
                    result.result_status = result_status
                    result.save()
                
                messages.success(request, 'Marks updated and result recalculated successfully!')
                
            else:
                # No Change
                req.status = 'REJECTED'
                req.save()
                messages.info(request, 'Revaluation request rejected. No changes made.')
                
        except Exception as e:
            messages.error(request, f'Error processing request: {str(e)}')
            
    return redirect('view_revaluation_requests')

# ==================== HELPER FUNCTIONS ====================

def check_controller_session(request):
    """Check if exam controller is logged in"""
    if 'user_id' in request.session and request.session.get('usertype', '').lower() == 'exam_controller':
        return True
    return False

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_system_action(user, action):
    """Log system action"""
    try:
        models.SystemLogs.objects.create(
            user=user,
            action=action,
            log_time=timezone.now()
        )
    except:
        pass


# ==================== PROFILE & PASSWORD ====================

def my_profile(request):
    """Display controller profile"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'controller/profile.html', context)

def edit_my_profile(request):
    """Display edit profile form"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'controller/edit_profile.html', context)

def update_my_profile(request):
    """Update profile logic"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        # Check if email taken
        if models.Users.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already taken by another user!')
            return redirect('edit_profile_controller')
            
        user.name = name
        user.email = email
        user.save()
        
        request.session['user_name'] = name
        request.session['semail'] = email
        
        log_system_action(user, f"Profile updated for Controller {user.name}")
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('controller_profile')
        
    return redirect('edit_profile_controller')

def change_password(request):
    """Display change password form"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    return render(request, 'controller/change_password.html')

def update_pass_controller(request):
    """Update password logic"""
    if not check_controller_session(request):
        return redirect('controller_login')
    
    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        if user.password != old_pass:
            messages.error(request, 'Incorrect old password!')
            return redirect('change_password_controller')
            
        if new_pass != confirm_pass:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password_controller')
            
        user.password = new_pass
        user.save()
        
        # Log action
        log_system_action(user, f"Password changed for user {user.name}")
        
        messages.success(request, 'Password updated successfully!')
        return redirect('controller_profile')
        
    return redirect('change_password_controller')

