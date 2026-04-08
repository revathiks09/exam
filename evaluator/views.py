
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from myproject import models

# ==================== AUTHENTICATION ====================

def check_evaluator_session(request):
    """Check if evaluator is logged in"""
    if 'user_id' in request.session and request.session.get('usertype', '').lower() == 'evaluator':
        return True
    return False

def evaluator_login(request):
    """Evaluator Login Page"""
    if check_evaluator_session(request):
        return redirect('evaluator_dashboard')
    return render(request, 'evaluator/login.html')

def evaluator_logout(request):
    """Evaluator Logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('home')

# ==================== DASHBOARD & SCRIPTS ====================

def dashboard(request):
    """Evaluator Dashboard - View Assigned Scripts"""
    return view_assigned_scripts(request)

def view_assigned_scripts(request):
    """View scripts assigned to the evaluator"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    eid = request.session['user_id']
    
    # Using Raw SQL for complex join as requested
    query = """
    SELECT m.id, u.name as student_name, s.subject_name, m.status, m.marks_obtained, m.updated_at
    FROM marks m
    JOIN users u ON m.student_id = u.id
    JOIN subjects s ON m.subject_id = s.id
    WHERE m.evaluator_id = %s
    ORDER BY m.id DESC
    """
    # Note: 'updated_at' might not exist in Marks model based on previous file view. 
    # Marks model had: student, subject, evaluator, marks_obtained, moderated_marks, status.
    # No updated_at. I will remove it.
    
    query = """
    SELECT m.id, u.name as student_name, s.subject_name, m.status, m.marks_obtained
    FROM marks m
    JOIN users u ON m.student_id = u.id
    JOIN subjects s ON m.subject_id = s.id
    WHERE m.evaluator_id = %s
    ORDER BY m.id DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [eid])
        columns = [col[0] for col in cursor.description]
        scripts = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
        
    context = {
        'scripts': scripts
    }
    return render(request, 'evaluator/scripts/assigned_scripts.html', context)

# ==================== MARKS MANAGEMENT ====================

def enter_marks(request, mid=None):
    """Form to enter/edit marks. mid is Marks ID (Script ID)"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
        
    # If mid is provided, we fetch the script details
    # The prompt separates enter_marks and edit_marks.
    # enter_marks might be for new entry? But assignment exists.
    # I'll treat enter_marks as valid for 'assigned' status.
    
    # Wait, simple CRUD pattern requested:
    # navigate with ID.
    
    scripts = [] 
    # If no ID, maybe show list? But view_assigned_scripts does that.
    # I'll assume enter_marks takes an ID or is a bulk form?
    # Given 'edit_marks' exists, enter_marks probably refers to the initial entry.
    
    # Only if mid is passed
    if mid:
        return edit_marks(request, mid) # Reuse edit for enter if it's the same form
        
    return redirect('view_assigned_scripts')

def edit_marks(request, mid):
    """Edit Marks Form"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
        
    try:
        script = models.Marks.objects.get(id=mid)
        
        if script.status and script.status.upper() == 'FINALIZED':
            messages.error(request, 'Cannot edit finalized marks!')
            return redirect('view_assigned_scripts')
            
        context = {
            'script': script,
            'student_name': script.student.name if script.student else 'Unknown',
            'subject_name': script.subject.subject_name if script.subject else 'Unknown'
        }
        return render(request, 'evaluator/marks/edit_marks.html', context)
    except models.Marks.DoesNotExist:
        messages.error(request, 'Invalid Script ID')
        return redirect('view_assigned_scripts')

def save_marks(request):
    """Save Marks (POST)"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
        
    if request.method == 'POST':
        mid = request.POST.get('mid')
        marks = request.POST.get('marks')
        
        try:
            obj = models.Marks.objects.get(id=mid)
            
            # Check status
            if obj.status and obj.status.upper() == 'FINALIZED':
                messages.error(request, 'Cannot save finalized marks!')
                return redirect('view_assigned_scripts')
                
            # Save external marks
            obj.external_marks = float(marks)
            
            # Calculate total
            inte = obj.internal_marks if obj.internal_marks is not None else 0
            obj.marks_obtained = float(marks) + float(inte)
            
            obj.status = 'Draft' 
            obj.save()
            messages.success(request, 'Marks saved successfully')
        except:
            messages.error(request, 'Error saving marks')
            
        return redirect('view_assigned_scripts')
    return redirect('view_assigned_scripts')

def update_marks(request):
    """Update Marks (POST)"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')

    if request.method == 'POST':
        mid = request.POST.get('mid')
        marks = request.POST.get('marks')
        
        try:
            obj = models.Marks.objects.get(id=mid)
            
            # Check status
            if obj.status and obj.status.upper() == 'FINALIZED':
                messages.error(request, 'Cannot update finalized marks!')
                return redirect('view_assigned_scripts')

            # Save external marks
            obj.external_marks = float(marks)
            
            # Calculate total
            inte = obj.internal_marks if obj.internal_marks is not None else 0
            obj.marks_obtained = float(marks) + float(inte)
            
            obj.save()
            messages.success(request, 'Marks updated successfully')
        except:
            messages.error(request, 'Error updating marks')
            
    return redirect('view_assigned_scripts')

# ==================== MODERATION & SUBMISSION ====================

def moderate_marks(request):
    """Moderate Marks view"""
    # Assuming this allows viewing marks that need moderation or performing moderation
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
        
    # List scripts that are 'submitted' or ready for moderation?
    # Or maybe this is the action to moderate?
    # Let's assume it's a list view for moderation if different from assigned.
    # Or maybe it's a specific action.
    
    # Given "Evaluation: moderate_marks()", and it's a list item alongside view_assigned_scripts.
    # I'll implement a view that lists scripts eligible for moderation (e.g. status='Submitted'?)
    
    eid = request.session['user_id']
    query = """
    SELECT m.id, u.name as student_name, s.subject_name, m.marks_obtained, m.moderated_marks
    FROM marks m
    JOIN users u ON m.student_id = u.id
    JOIN subjects s ON m.subject_id = s.id
    WHERE m.evaluator_id = %s AND UPPER(m.status) = 'FINALIZED'
    """
    # Adjust logic as needed. If Evaluator does moderation, maybe they moderate others' marks?
    # Or maybe 'moderate_marks' is a function to APPLY moderation (POST).
    # I'll implement as a view which renders a list or form.
    
    with connection.cursor() as cursor:
        cursor.execute(query, [eid])
        columns = [col[0] for col in cursor.description]
        scripts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    context = {'scripts': scripts}
    return render(request, 'evaluator/marks/moderate_marks.html', context)

def apply_moderation(request):
    """Apply moderation to marks"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    if request.method == 'POST':
        mid = request.POST.get('mid')
        moderated_marks = request.POST.get('moderated_marks')
        
        try:
            obj = models.Marks.objects.get(id=mid)
            
            # Check if evaluator owns this script
            if obj.evaluator_id != request.session['user_id']:
                messages.error(request, 'Unauthorized action!')
                return redirect('moderate_marks')
            
            obj.moderated_marks = moderated_marks
            obj.save()
            messages.success(request, 'Moderation applied successfully!')
        except Exception as e:
            messages.error(request, f'Error applying moderation: {str(e)}')
    
    return redirect('moderate_marks')

def submit_final_marks(request):
    """Submit final marks (Freeze)"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
        
    if request.method == 'POST':
        mid_list = request.POST.getlist('mid') # List of IDs to submit
        
        # Or simple single submission
        mid = request.POST.get('mid')
        if mid:
            try:
                obj = models.Marks.objects.get(id=mid)
                obj.status = 'Finalized'
                obj.save()
                messages.success(request, 'Marks finalized successfully')
            except:
                messages.error(request, 'Error finalizing marks')
        
    return redirect('view_assigned_scripts')

# ==================== PROFILE & PASSWORD ====================

def my_profile(request):
    """Display evaluator profile"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'evaluator/profile.html', context)

def edit_my_profile(request):
    """Display edit profile form"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    user = models.Users.objects.get(id=request.session['user_id'])
    context = {'user': user}
    return render(request, 'evaluator/edit_profile.html', context)

def update_my_profile(request):
    """Update profile logic"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        # Check if email taken
        if models.Users.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already taken by another user!')
            return redirect('edit_profile_evaluator')
            
        user.name = name
        user.email = email
        user.save()
        
        request.session['user_name'] = name
        request.session['semail'] = email
        
        try:
            models.SystemLogs.objects.create(
                user=user,
                action=f"Profile updated for Evaluator {user.name}",
                log_time=timezone.now()
            )
        except:
            pass
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('evaluator_profile')
        
    return redirect('edit_profile_evaluator')

def change_password(request):
    """Display change password form"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    return render(request, 'evaluator/change_password.html')

def update_pass_evaluator(request):
    """Update password logic"""
    if not check_evaluator_session(request):
        return redirect('evaluator_login')
    
    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        
        user = models.Users.objects.get(id=request.session['user_id'])
        
        if user.password != old_pass:
            messages.error(request, 'Incorrect old password!')
            return redirect('change_password_evaluator')
            
        if new_pass != confirm_pass:
            messages.error(request, 'New passwords do not match!')
            return redirect('change_password_evaluator')
            
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
        return redirect('evaluator_profile')
        
    return redirect('change_password_evaluator')
