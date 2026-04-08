from django.shortcuts import render, redirect
from django.contrib import messages
from . import models
from django.utils import timezone

def home(request):
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

# ==================== COMMON AUTHENTICATION ====================

def login_page(request):
    """Display common login page"""
    if 'user_id' in request.session:
        # Redirect if already logged in based on role
        role = request.session.get('usertype', '').lower()
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'exam_controller':
            return redirect('controller_dashboard')
        # Add other role redirects here as they are implemented
        
    return render(request, 'home/login.html')

def check_login(request):
    """Verify credentials for all user types"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Check for user with given credentials
            user = models.Users.objects.get(email=email, password=password)
            
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
                log_system_action(user, f"User {user.name} ({user.role}) logged in")
                
                messages.success(request, f'Welcome back, {user.name}!')
                
                # Redirect based on role
                # Redirect based on role
                role = user.role.lower()
                if role == 'admin':
                    return redirect('admin_dashboard')
                elif role == 'exam_controller':
                    return redirect('controller_dashboard')
                elif role == 'faculty':
                    return redirect('faculty_dashboard') 
                elif role == 'evaluator':
                    return redirect('evaluator_dashboard')
                elif role == 'student':
                    return redirect('student_dashboard')
                else:
                    return redirect('home')
                    
            else:
                messages.error(request, 'Your account is deactivated. Please contact support.')
                return redirect('login_page')
                
        except models.Users.DoesNotExist:
            messages.error(request, 'Invalid email or password!')
            return redirect('login_page')
            
    return redirect('login_page')

def logout_user(request):
    """Common logout function"""
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
            log_system_action(user, f"User {user.name} logged out")
            
        except:
            pass
    
    # Clear session
    request.session.flush()
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login_page')

# ==================== HELPER FUNCTIONS ====================

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