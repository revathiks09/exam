from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('check_login/', views.check_admin_login, name='check_admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.my_profile, name='admin_profile'),
    path('edit_profile/', views.edit_my_profile, name='edit_profile_admin'),
    path('update_profile/', views.update_my_profile, name='update_profile_admin'),
    
    # User Management
    path('users/', views.users, name='users'),
    path('add_user/', views.add_user, name='add_user'),
    path('save_user/', views.save_user, name='save_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('update_user/', views.update_user, name='update_user'),
    path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    # Student Management
    path('students/', views.students, name='students'),
    path('add_student/', views.add_student, name='add_student'),
    path('save_student/', views.save_student, name='save_student'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('update_student/', views.update_student, name='update_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    
    # Department Management
    path('departments/', views.departments, name='departments'),
    path('add_department/', views.add_department, name='add_department'),
    path('save_department/', views.save_department, name='save_department'),
    path('edit_department/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('update_department/', views.update_department, name='update_department'),
    path('delete_department/<int:dept_id>/', views.delete_department, name='delete_department'),
    
    # Course Management
    path('courses/', views.courses, name='courses'),
    path('add_course/', views.add_course, name='add_course'),
    path('save_course/', views.save_course, name='save_course'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('update_course/', views.update_course, name='update_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    
    # Semester Management
    path('semesters/', views.semesters, name='semesters'),
    path('add_semester/', views.add_semester, name='add_semester'),
    path('save_semester/', views.save_semester, name='save_semester'),
    path('edit_semester/<int:semester_id>/', views.edit_semester, name='edit_semester'),
    path('update_semester/', views.update_semester, name='update_semester'),
    path('delete_semester/<int:semester_id>/', views.delete_semester, name='delete_semester'),

    # Subject Management
    path('subjects/', views.subjects, name='subjects'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('save_subject/', views.save_subject, name='save_subject'),
    path('edit_subject/<int:sub_id>/', views.edit_subject, name='edit_subject'),
    path('update_subject/', views.update_subject, name='update_subject'),
    path('delete_subject/<int:sub_id>/', views.delete_subject, name='delete_subject'),
    
    # System Management & Reports
    path('academic_reports/', views.generate_academic_reports, name='academic_reports'),
    path('result_statistics/', views.view_result_statistics, name='result_statistics'),
    path('backup_database/', views.backup_database, name='backup_database'),
    path('restore_database/', views.restore_database, name='restore_database'),
    path('system_logs/', views.system_logs, name='system_logs'),
    
    # Password Management
    path('change_password/', views.change_password, name='change_password'),
    path('update_pass_admin/', views.update_pass_admin, name='update_pass_admin'),
]
