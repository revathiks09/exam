from django.shortcuts import render, redirect
from django.contrib import messages
from myproject import models
from django.db import connection
from django.utils import timezone
from datetime import datetime
import json

# ==================== AUTHENTICATION ====================

def admin_login(request):
    """Display admin login page"""
    return render(request, 'admin/login.html')

def check_admin_login(request):
    """Verify admin credentials and create session"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = models.Users.objects.get(email=email, password=password, role='admin')
            
            if user.status == 1:  # Active user
                # Create session
                request.session['user_id'] = user.id
                request.session['semail'] = user.email
                request.session['user_name'] = user.name
                request.session['usertype'] = user.role
                
                # Save session explicitly
                request.session.save()
                
                # Debug: Print session data
                print(f"✅ Session created for user: {user.email}")
                print(f"   Session data: {dict(request.session)}")
                print(f"   Session key: {request.session.session_key}")
                
                # Log login session
                models.LoginSessions.objects.create(
                    user=user,
                    login_time=timezone.now(),
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Log system action
                log_system_action(user, f"Admin {user.name} logged in")
                
                messages.success(request, f'Welcome back, {user.name}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Your account is deactivated. Please contact support.')
                return redirect('admin_login')
                
        except models.Users.DoesNotExist:
            messages.error(request, 'Invalid email or password!')
            return redirect('admin_login')
    
    return redirect('admin_login')

def admin_logout(request):
    """Logout admin and clear session"""
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
            log_system_action(user, f"Admin {user.name} logged out")
            
        except:
            pass
    
    # Clear session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

# ==================== DASHBOARD ====================

def admin_dashboard(request):
    """Admin dashboard with statistics"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Get statistics
    total_users = models.Users.objects.count()
    total_students = models.Users.objects.filter(role='student').count()
    total_faculty = models.Users.objects.filter(role='faculty').count()
    total_evaluators = models.Users.objects.filter(role='evaluator').count()
    
    total_departments = models.Departments.objects.filter(status=1).count()
    total_courses = models.Courses.objects.filter(status=1).count()
    total_semesters = models.Semesters.objects.count()
    total_subjects = models.Subjects.objects.count()
    
    # Recent users
    recent_users = models.Users.objects.order_by('-created_at')[:5]
    
    # Recent login sessions
    recent_logins = models.LoginSessions.objects.select_related('user').order_by('-login_time')[:10]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_evaluators': total_evaluators,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_semesters': total_semesters,
        'total_subjects': total_subjects,
        'recent_users': recent_users,
        'recent_logins': recent_logins,
    }
    
    return render(request, 'admin/index.html', context)

def my_profile(request):
    """Display admin profile"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'admin/profile.html', context)

def edit_my_profile(request):
    """Display edit profile form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'admin/edit_profile.html', context)

def update_my_profile(request):
    """Update profile logic"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        # Check if email taken by another user
        if models.Users.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already taken by another user!')
            return redirect('edit_profile_admin')
            
        user.name = name
        user.email = email
        user.save()
        
        # Update session if name changed
        request.session['user_name'] = name
        request.session['semail'] = email
        
        models.SystemLogs.objects.create(
            user=user,
            action=f"Profile updated for Admin {user.name}",
            log_time=timezone.now()
        )
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')
        
    return redirect('edit_profile_admin')

# ==================== USER MANAGEMENT ====================

def users(request):
    """List all users"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user_list = models.Users.objects.all().order_by('-created_at')
    context = {'users': user_list}
    return render(request, 'admin/users/users.html', context)

def add_user(request):
    """Display add user form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    return render(request, 'admin/users/add_user.html')

def save_user(request):
    """Save new user"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        status = request.POST.get('status', 1)
        
        # Check if email already exists
        if models.Users.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('add_user')
        
        # Create user
        user = models.Users.objects.create(
            name=name,
            email=email,
            password=password,  # In production, use hashing
            role=role,
            status=status,
            created_at=timezone.now()
        )
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Created new user: {name} ({role})")
        
        messages.success(request, f'User {name} created successfully!')
        return redirect('users')
    
    return redirect('add_user')

def edit_user(request, user_id):
    """Display edit user form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user = models.Users.objects.get(id=user_id)
    context = {'user': user}
    return render(request, 'admin/users/edit_user.html', context)

def update_user(request):
    """Update user details"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = models.Users.objects.get(id=user_id)
        
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        
        # Update password only if provided
        new_password = request.POST.get('password')
        if new_password:
            user.password = new_password
        
        user.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Updated user: {user.name}")
        
        messages.success(request, 'User updated successfully!')
        return redirect('users')
    
    return redirect('users')

def activate_user(request, user_id):
    """Activate a user"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user = models.Users.objects.get(id=user_id)
    user.status = 1
    user.save()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Activated user: {user.name}")
    
    messages.success(request, f'User {user.name} activated successfully!')
    return redirect('users')

def deactivate_user(request, user_id):
    """Deactivate a user"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user = models.Users.objects.get(id=user_id)
    user.status = 0
    user.save()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Deactivated user: {user.name}")
    
    messages.warning(request, f'User {user.name} deactivated successfully!')
    return redirect('users')

def delete_user(request, user_id):
    """Delete a user"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    user = models.Users.objects.get(id=user_id)
    user_name = user.name
    user.delete()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Deleted user: {user_name}")
    
    messages.success(request, f'User {user_name} deleted successfully!')
    return redirect('users')

# ==================== STUDENT MANAGEMENT ====================

def students(request):
    """List all students with academic details"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Fetch students joined with user and related academic tables
    student_list = models.Students.objects.select_related('user', 'dept', 'course', 'semester').all().order_by('-created_at')
    context = {'students': student_list}
    return render(request, 'admin/students/students.html', context)

def add_student(request):
    """Display add student form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    departments = models.Departments.objects.filter(status=1)
    courses = models.Courses.objects.filter(status=1)
    semesters = models.Semesters.objects.select_related('course').all().order_by('semester_no')
    
    context = {
        'departments': departments,
        'courses': courses,
        'semesters': semesters
    }
    return render(request, 'admin/students/add_student.html', context)

def save_student(request):
    """Save new student (User + Student details)"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        # User details
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        status = request.POST.get('status', 1)
        
        # Academic details
        regno = request.POST.get('regno')
        dept_id = request.POST.get('dept_id')
        course_id = request.POST.get('course_id')
        semester_id = request.POST.get('semester_id')
        
        # Check if email exists
        if models.Users.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('add_student')

        # Check if regno already exists
        if models.Students.objects.filter(regno=regno).exists():
            messages.error(request, f'Registration Number {regno} already exists!')
            return redirect('add_student')
            
        try:
            # 1. Create User
            user = models.Users.objects.create(
                name=name,
                email=email,
                password=password, # Use hashing in production
                role='student',
                status=status,
                created_at=timezone.now()
            )
            
            # 2. Create Student Linked to User
            models.Students.objects.create(
                user=user,
                regno=regno,
                dept_id=dept_id,
                course_id=course_id,
                semester_id=semester_id,
                created_at=timezone.now()
            )
            
            # Log action
            current_user = models.Users.objects.get(id=request.session['user_id'])
            log_system_action(current_user, f"Created student: {name} ({regno})")
            
            messages.success(request, f'Student {name} added successfully!')
            return redirect('students')
            
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}')
            return redirect('add_student')
            
    return redirect('add_student')

def edit_student(request, student_id):
    """Display edit student form"""
    if not check_admin_session(request):
        return redirect('admin_login')

    student = models.Students.objects.select_related('user').get(id=student_id)
    departments = models.Departments.objects.filter(status=1)
    courses = models.Courses.objects.filter(status=1)
    semesters = models.Semesters.objects.select_related('course').all().order_by('semester_no')

    context = {
        'student': student,
        'departments': departments,
        'courses': courses,
        'semesters': semesters
    }
    return render(request, 'admin/students/edit_student.html', context)

def update_student(request):
    """Update student details"""
    if not check_admin_session(request):
        return redirect('admin_login')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = models.Students.objects.select_related('user').get(id=student_id)
        user = student.user
        
        # Update User details
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.status = request.POST.get('status')
        if request.POST.get('password'):
            user.password = request.POST.get('password')
        user.save()
        
        # Update Student details
        student.regno = request.POST.get('regno')
        student.dept_id = request.POST.get('dept_id')
        student.course_id = request.POST.get('course_id')
        student.semester_id = request.POST.get('semester_id')
        student.updated_at = timezone.now()
        student.save()
        
        messages.success(request, 'Student updated successfully!')
        return redirect('students')
        
    return redirect('students')

def delete_student(request, student_id):
    """Delete student (and user record)"""
    if not check_admin_session(request):
        return redirect('admin_login')
        
    try:
        student = models.Students.objects.select_related('user').get(id=student_id)
        user = student.user
        name = user.name
        
        # Deleting user will cascade delete student due to DB constraint, 
        # but Django usually handles this. If constraint exists, deleting user is enough.
        # However, to be safe and if managed=False, we might need manual delete if no constraint.
        # The script created FK with ON DELETE CASCADE.
        user.delete() 
        
        messages.success(request, f'Student {name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting student: {str(e)}')
        
    return redirect('students')

# ==================== DEPARTMENT MANAGEMENT ====================

def departments(request):
    """List all departments"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    dept_list = models.Departments.objects.all()
    context = {'departments': dept_list}
    return render(request, 'admin/departments/departments.html', context)

def add_department(request):
    """Display add department form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    return render(request, 'admin/departments/add_department.html')

def save_department(request):
    """Save new department"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        dept_name = request.POST.get('dept_name')
        status = request.POST.get('status', 1)
        
        # Check if department already exists
        if models.Departments.objects.filter(dept_name=dept_name).exists():
            messages.error(request, f'Department {dept_name} already exists!')
            return redirect('add_department')

        # Create department
        dept = models.Departments.objects.create(
            dept_name=dept_name,
            status=status
        )
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Created department: {dept_name}")
        
        messages.success(request, f'Department {dept_name} created successfully!')
        return redirect('departments')
    
    return redirect('add_department')

def edit_department(request, dept_id):
    """Display edit department form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    dept = models.Departments.objects.get(id=dept_id)
    context = {'department': dept}
    return render(request, 'admin/departments/edit_department.html', context)

def update_department(request):
    """Update department"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        dept_id = request.POST.get('dept_id')
        dept = models.Departments.objects.get(id=dept_id)
        
        dept.dept_name = request.POST.get('dept_name')
        dept.status = request.POST.get('status')
        dept.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Updated department: {dept.dept_name}")
        
        messages.success(request, 'Department updated successfully!')
        return redirect('departments')
    
    return redirect('departments')

def delete_department(request, dept_id):
    """Delete department"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    dept = models.Departments.objects.get(id=dept_id)
    dept_name = dept.dept_name
    dept.delete()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Deleted department: {dept_name}")
    
    messages.success(request, f'Department {dept_name} deleted successfully!')
    return redirect('departments')

# ==================== COURSE MANAGEMENT ====================

def courses(request):
    """List all courses"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    course_list = models.Courses.objects.raw("select * from Courses c join Departments d on (d.id=c.dept_id)")
    context = {'courses': course_list}
    return render(request, 'admin/courses/courses.html', context)

def add_course(request):
    """Display add course form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    departments = models.Departments.objects.all()
    context = {'departments': departments}
    return render(request, 'admin/courses/add_course.html', context)

def save_course(request):
    """Save new course"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        dept_id = request.POST.get('dept_id')
        status = request.POST.get('status', 1)
        
        # Check if course already exists in this department
        if models.Courses.objects.filter(course_name=course_name, dept_id=dept_id).exists():
            dept_name = models.Departments.objects.get(id=dept_id).dept_name
            messages.error(request, f'Course {course_name} already exists in {dept_name}!')
            return redirect('add_course')

        # Create course using object instantiation
        course = models.Courses(
            course_name=course_name,
            dept_id=dept_id,
            status=status
        )
        course.save()
        
        # Log action
        
        messages.success(request, f'Course {course_name} created successfully!')
        return redirect('courses')
    
    return redirect('add_course')

def edit_course(request, course_id):
    """Display edit course form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    course = models.Courses.objects.get(id=course_id)
    departments = models.Departments.objects.all()
    context = {'course': course, 'departments': departments}
    return render(request, 'admin/courses/edit_course.html', context)

def update_course(request):
    """Update course"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = models.Courses.objects.get(id=course_id)
        
        course.course_name = request.POST.get('course_name')
        course.dept_id = request.POST.get('dept_id')
        course.status = request.POST.get('status')
        course.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Updated course: {course.course_name}")
        
        messages.success(request, 'Course updated successfully!')
        return redirect('courses')
    
    return redirect('courses')

def delete_course(request, course_id):
    """Delete course"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    course = models.Courses.objects.get(id=course_id)
    course_name = course.course_name
    course.delete()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Deleted course: {course_name}")
    
    messages.success(request, f'Course {course_name} deleted successfully!')
    return redirect('courses')

# ==================== SEMESTER MANAGEMENT ====================

def semesters(request):
    """List all semesters"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    semester_list = models.Semesters.objects.select_related('course').all()
    context = {'semesters': semester_list}
    return render(request, 'admin/semesters/semesters.html', context)

def add_semester(request):
    """Display add semester form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    courses = models.Courses.objects.select_related('dept').filter(status=1)
    context = {'courses': courses}
    return render(request, 'admin/semesters/add_semester.html', context)

def save_semester(request):
    """Save new semester"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        semester_no = request.POST.get('semester_no')
        
        course = models.Courses.objects.get(id=course_id)

        # Check if semester already exists for this course
        if models.Semesters.objects.filter(course=course, semester_no=semester_no).exists():
            messages.error(request, f'Semester {semester_no} already exists for {course.course_name}!')
            return redirect('add_semester')
        
        # Create semester
        semester = models.Semesters.objects.create(
            course=course,
            semester_no=semester_no
        )
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Created semester {semester_no} for {course.course_name}")
        
        messages.success(request, f'Semester {semester_no} created successfully!')
        return redirect('semesters')
    
    return redirect('add_semester')

def edit_semester(request, semester_id):
    """Display edit semester form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    semester = models.Semesters.objects.get(id=semester_id)
    courses = models.Courses.objects.select_related('dept').filter(status=1)
    context = {'semester': semester, 'courses': courses}
    return render(request, 'admin/semesters/edit_semester.html', context)

def update_semester(request):
    """Update semester"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        semester_id = request.POST.get('semester_id')
        semester = models.Semesters.objects.get(id=semester_id)
        
        course_id = request.POST.get('course_id')
        semester.course = models.Courses.objects.get(id=course_id)
        semester.semester_no = request.POST.get('semester_no')
        semester.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Updated semester {semester.semester_no}")
        
        messages.success(request, 'Semester updated successfully!')
        return redirect('semesters')
    
    return redirect('semesters')

def delete_semester(request, semester_id):
    """Delete semester"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    semester = models.Semesters.objects.get(id=semester_id)
    semester_no = semester.semester_no
    semester.delete()
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, f"Deleted semester {semester_no}")
    
    messages.success(request, f'Semester {semester_no} deleted successfully!')
    return redirect('semesters')

# ==================== SYSTEM MANAGEMENT ====================

def generate_academic_reports(request):
    """Generate academic reports"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Calculate and update analytics
    subjects = models.Subjects.objects.all()
    
    for subject in subjects:
        # Get results for this subject
        # Link: Result -> Semester -> Subject (via Semester)
        # We need marks to link Result/Student to Subject performance
        
        # Calculate pass percentage for this subject based on Marks
        marks = models.Marks.objects.filter(subject=subject, status__iexact='Approved')
        total_students = marks.count()
        
        if total_students > 0:
            pass_count = 0
            total_score = 0
            grades = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
            
            for mark in marks:
                score = mark.moderated_marks or mark.marks_obtained or 0
                total_score += score
                
                # Simple grading for distribution
                perc = score # Assuming score is out of 100
                if perc >= 90: grade = 'A+'
                elif perc >= 80: grade = 'A'
                elif perc >= 70: grade = 'B+'
                elif perc >= 60: grade = 'B'
                elif perc >= 50: grade = 'C'
                elif perc >= 40: grade = 'D'
                else: grade = 'F'
                
                grades[grade] += 1
                if perc >= 40:
                    pass_count += 1
            
            pass_percentage = (pass_count / total_students) * 100
            avg_score = total_score / total_students
            
            # Convert grades dict to string: "A+: 2, A: 5, ..."
            grade_dist_str = ", ".join([f"{g}: {c}" for g, c in grades.items() if c > 0])
            
            # Update or create analytics record
            models.ResultAnalytics.objects.update_or_create(
                subject=subject,
                defaults={
                    'pass_percentage': pass_percentage,
                    'average_marks': avg_score,
                    'grade_distribution': grade_dist_str,
                    'generated_at': timezone.now()
                }
            )
            
    # Get result analytics
    analytics = models.ResultAnalytics.objects.select_related('subject').order_by('-generated_at')
    
    context = {'analytics': analytics}
    return render(request, 'admin/reports/academic_reports.html', context)

def view_result_statistics(request):
    """View result statistics"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Get statistics
    total_results = models.Results.objects.count()
    pass_count = models.Results.objects.filter(result_status__iexact='pass').count()
    fail_count = models.Results.objects.filter(result_status__iexact='fail').count()
    
    # Grade distribution
    grade_stats = {}
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT grade, COUNT(*) as count 
            FROM results 
            GROUP BY grade
        """)
        for row in cursor.fetchall():
            grade_stats[row[0]] = row[1]
    
    # Subject-wise statistics
    subject_stats = models.ResultAnalytics.objects.select_related('subject').all()
    
    context = {
        'total_results': total_results,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_percentage': (pass_count / total_results * 100) if total_results > 0 else 0,
        'grade_stats': grade_stats,
        'subject_stats': subject_stats,
    }
    
    return render(request, 'admin/reports/result_statistics.html', context)

def backup_database(request):
    """Backup database"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, "Database backup initiated")
    
    messages.info(request, 'Database backup initiated. This feature requires server-side configuration.')
    return redirect('admin_dashboard')

def restore_database(request):
    """Restore database"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Log action
    current_user = models.Users.objects.get(id=request.session['user_id'])
    log_system_action(current_user, "Database restore initiated")
    
    messages.info(request, 'Database restore initiated. This feature requires server-side configuration.')
    return redirect('admin_dashboard')

def system_logs(request):
    """View system logs"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    logs = models.SystemLogs.objects.select_related('user').order_by('-log_time')[:100]
    context = {'logs': logs}
    return render(request, 'admin/system/system_logs.html', context)

def change_password(request):
    """Display change password form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    return render(request, 'admin/change_password.html')

def update_pass_admin(request):
    """Update admin password"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        if user.password != old_password:
            messages.error(request, 'Old password is incorrect!')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password')
        
        user.password = new_password
        user.save()
        
        # Log action
        log_system_action(user, "Changed password")
        
        messages.success(request, 'Password changed successfully!')
        return redirect('admin_dashboard')
    
    return redirect('change_password')

# ==================== HELPER FUNCTIONS ====================

def check_admin_session(request):
    """Check if admin is logged in"""
    if 'user_id' in request.session and request.session.get('usertype', '').lower() == 'admin':
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

# ==================== SUBJECT MANAGEMENT ====================

def subjects(request):
    """List all subjects"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Select related for efficiency
    subject_list = models.Subjects.objects.select_related('semester', 'faculty').all()
    context = {'subjects': subject_list}
    return render(request, 'admin/subjects/subjects.html', context)

def add_subject(request):
    """Display add subject form"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    # Need semesters to assign subject to
    semesters = models.Semesters.objects.select_related('course').all()
    # Need faculty to assign subject to
    faculty_list = models.Users.objects.filter(role='faculty')
    
    context = {
        'semesters': semesters, 
        'faculty_list': faculty_list
    }
    return render(request, 'admin/subjects/add_subject.html', context)

def save_subject(request):
    """Save new subject"""
    if not check_admin_session(request):
        return redirect('admin_login')
    
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        semester_id = request.POST.get('semester_id')
        faculty_id = request.POST.get('faculty_id')
        
        semester = models.Semesters.objects.get(id=semester_id)
        faculty = models.Users.objects.get(id=faculty_id)
        
        # Check if subject already exists in this semester
        if models.Subjects.objects.filter(subject_name=subject_name, semester=semester).exists():
            messages.error(request, f'Subject {subject_name} already exists in Semester {semester.semester_no}!')
            return redirect('add_subject')

        # Create subject using pure object pattern
        subject = models.Subjects()
        subject.subject_name = subject_name
        subject.semester = semester
        subject.faculty = faculty
        subject.save()
        
        # Log action
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Created subject: {subject_name} for Sem {semester.semester_no}")
        
        messages.success(request, f'Subject {subject_name} created successfully!')
        return redirect('subjects')
    
    return redirect('add_subject')

def delete_subject(request, sub_id):
    """Delete subject"""
    if not check_admin_session(request):
        return redirect('admin_login')
        
    try:
        subject = models.Subjects.objects.get(id=sub_id)
        sub_name = subject.subject_name
        subject.delete()
        
        # Log
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Deleted subject: {sub_name}")
        
        messages.success(request, 'Subject deleted successfully')
    except:
        messages.error(request, 'Error deleting subject')
        
    return redirect('subjects')

def edit_subject(request, sub_id):
    """Display edit subject form"""
    if not check_admin_session(request):
        return redirect('admin_login')
        
    subject = models.Subjects.objects.get(id=sub_id)
    # Fetch options
    semesters = models.Semesters.objects.select_related('course').all()
    faculty_list = models.Users.objects.filter(role='faculty')
    
    context = {
        'subject': subject,
        'semesters': semesters,
        'faculty_list': faculty_list
    }
    return render(request, 'admin/subjects/edit_subject.html', context)

def update_subject(request):
    """Update subject"""
    if not check_admin_session(request):
        return redirect('admin_login')
        
    if request.method == 'POST':
        sub_id = request.POST.get('sub_id')
        subject = models.Subjects.objects.get(id=sub_id)
        
        subject.subject_name = request.POST.get('subject_name')
        semester_id = request.POST.get('semester_id')
        faculty_id = request.POST.get('faculty_id')
        
        subject.semester = models.Semesters.objects.get(id=semester_id)
        subject.faculty = models.Users.objects.get(id=faculty_id)
        
        subject.save()
        
        # Log
        current_user = models.Users.objects.get(id=request.session['user_id'])
        log_system_action(current_user, f"Updated subject: {subject.subject_name}")
        
        messages.success(request, 'Subject updated successfully')
        return redirect('subjects')
        
    return redirect('subjects')