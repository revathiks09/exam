from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='faculty_dashboard'),
    
    # Question Paper Management
    path('add_question_paper/', views.add_question_paper, name='add_question_paper'),
    path('save_question_paper/', views.save_question_paper, name='save_question_paper'),
    path('view_question_papers/', views.view_question_papers, name='view_question_papers'),
    path('edit_question_paper/<int:qpid>/', views.edit_question_paper, name='edit_question_paper'),
    path('update_question_paper/', views.update_question_paper, name='update_question_paper'),
    path('submit_for_approval/<int:qpid>/', views.submit_for_approval, name='submit_for_approval'),
    
    # Assessment (Internal Marks)
    path('enter_internal_marks/', views.enter_internal_marks, name='enter_internal_marks'),
    path('save_internal_marks/', views.save_internal_marks, name='save_internal_marks'),
    path('update_internal_marks/', views.update_internal_marks, name='update_internal_marks'),
    path('manage_internal_marks/', views.manage_internal_marks, name='manage_internal_marks'),
    path('delete_internal_marks/<int:sub_id>/', views.delete_internal_marks, name='delete_internal_marks'),
    path('delete_student_mark/<int:mark_id>/', views.delete_student_mark, name='delete_student_mark'),

    
    # Analytics
    path('view_subject_performance/', views.view_subject_performance, name='view_subject_performance'),
    
    # Profile & Password
    path('profile/', views.my_profile, name='faculty_profile'),
    path('edit_profile/', views.edit_my_profile, name='edit_profile_faculty'),
    path('update_profile/', views.update_my_profile, name='update_profile_faculty'),
    path('change_password/', views.change_password, name='change_password_faculty'),
    path('update_password/', views.update_pass_faculty, name='update_pass_faculty'),
]
