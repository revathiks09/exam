from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.controller_login, name='controller_login'),
    path('check_login/', views.check_controller_login, name='check_controller_login'),
    path('logout/', views.controller_logout, name='controller_logout'),
    
    # Dashboard
    path('dashboard/', views.controller_dashboard, name='controller_dashboard'),

    # Question Paper Control
    path('submitted_papers/', views.view_submitted_papers, name='view_submitted_papers'),
    path('approve_paper/<int:paper_id>/', views.approve_question_paper, name='approve_question_paper'),
    path('reject_paper/<int:paper_id>/', views.reject_question_paper, name='reject_question_paper'),
    
    # Exam Management
    path('create_schedule/', views.create_exam_schedule, name='create_exam_schedule'),
    path('save_schedule/', views.save_exam_schedule, name='save_exam_schedule'),
    path('edit_schedule/<int:schedule_id>/', views.edit_exam_schedule, name='edit_exam_schedule'),
    path('update_schedule/', views.update_exam_schedule, name='update_exam_schedule'),
    path('delete_schedule/<int:schedule_id>/', views.delete_exam_schedule, name='delete_exam_schedule'),
    path('exam_timetable/', views.publish_exam_timetable, name='exam_timetable'),
    path('generate_seating/', views.generate_seating_arrangement, name='generate_seating'),
    path('view_seating/', views.view_seating_arrangement, name='controller_view_seating'),
    path('generate_hall_ticket/', views.generate_hall_ticket, name='generate_hall_ticket'),
    path('view_hall_tickets/', views.view_hall_tickets, name='view_hall_tickets'),
    
    # Evaluator Assignment
    path('assign_evaluator/', views.assign_evaluator, name='assign_evaluator'),
    path('view_assignments/', views.view_assignments, name='view_assignments'),
    path('edit_assignment/<int:subject_id>/<int:evaluator_id>/', views.edit_assignment, name='edit_assignment'),
    
    # Mark Approval
    path('pending_marks/', views.view_pending_marks, name='view_pending_marks'),
    path('approve_marks/', views.approve_marks, name='approve_marks'),
    path('reject_marks/<int:mark_id>/', views.reject_marks, name='reject_marks'),
    
    # Result Supervision
    path('monitor_marks/', views.monitor_mark_entry, name='monitor_mark_entry'),
    path('approve_results/', views.approve_final_results, name='approve_final_results'),
    path('view_results/', views.view_results, name='view_results'),
    
    # Revaluation
    path('revaluation_requests/', views.view_revaluation_requests, name='view_revaluation_requests'),
    path('process_revaluation/', views.process_revaluation, name='process_revaluation'),
    
    # Profile & Password
    path('profile/', views.my_profile, name='controller_profile'),
    path('edit_profile/', views.edit_my_profile, name='edit_profile_controller'),
    path('update_profile/', views.update_my_profile, name='update_profile_controller'),
    path('change_password/', views.change_password, name='change_password_controller'),
    path('update_password/', views.update_pass_controller, name='update_pass_controller'),
    path('change_password/', views.change_password, name='change_password_controller'),
    path('update_password/', views.update_pass_controller, name='update_pass_controller'),
]
