
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    
    # Dashboard & Exams
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('timetable/', views.view_exam_timetable, name='view_exam_timetable'),
    path('hall_ticket/', views.download_hall_ticket, name='download_hall_ticket'),
    path('hall_ticket/view/<int:ht_id>/', views.view_hall_ticket_detail, name='view_hall_ticket_detail'),
    path('seating/', views.view_seating_arrangement, name='view_seating_arrangement'),
    
    # Results
    path('results/', views.view_result, name='view_result'),
    path('grade_sheet/<int:rid>/', views.download_grade_sheet, name='download_grade_sheet'),
    path('performance/', views.view_performance_history, name='view_performance_history'),
    
    # Revaluation
    path('revaluation/apply/', views.apply_revaluation, name='apply_revaluation'),
    path('revaluation/status/', views.track_revaluation_status, name='track_revaluation_status'),
    
    # Profile & Password
    path('profile/', views.my_profile, name='student_profile'),
    path('edit_profile/', views.edit_my_profile, name='edit_profile_student'),
    path('update_profile/', views.update_my_profile, name='update_profile_student'),
    path('change_password/', views.change_password, name='change_password_student'),
    path('update_password/', views.update_pass_student, name='update_pass_student'),
]
