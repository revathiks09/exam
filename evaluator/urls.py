
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.evaluator_login, name='evaluator_login'),
    path('logout/', views.evaluator_logout, name='evaluator_logout'),
    
    # Dashboard & Assessment
    path('dashboard/', views.dashboard, name='evaluator_dashboard'),
    path('scripts/', views.view_assigned_scripts, name='view_assigned_scripts'),
    
    # Marks CRUD
    path('enter_marks/<int:mid>/', views.enter_marks, name='enter_marks'), # If creating new, but here using ID
    path('save_marks/', views.save_marks, name='save_marks'),
    path('edit_marks/<int:mid>/', views.edit_marks, name='edit_marks'),
    path('update_marks/', views.update_marks, name='update_marks'),
    
    # Moderation
    path('moderate/', views.moderate_marks, name='moderate_marks'),
    path('apply_moderation/', views.apply_moderation, name='apply_moderation'),
    path('submit_final/', views.submit_final_marks, name='submit_final_marks'),
    
    # Profile & Password
    path('profile/', views.my_profile, name='evaluator_profile'),
    path('edit_profile/', views.edit_my_profile, name='edit_profile_evaluator'),
    path('update_profile/', views.update_my_profile, name='update_profile_evaluator'),
    path('change_password/', views.change_password, name='change_password_evaluator'),
    path('update_password/', views.update_pass_evaluator, name='update_pass_evaluator'),
]
