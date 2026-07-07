from django.urls import path
from . import views

urlpatterns = [
    # Main builder page
    path('resume/', views.resume_builder, name='resume_builder'),

    # Personal info + photo
    path('resume/save/personal/', views.resume_save_personal, name='resume_save_personal'),
    path('resume/upload/photo/', views.resume_upload_photo, name='resume_upload_photo'),

    # Section CRUD
    path('resume/save/section/', views.resume_save_section, name='resume_save_section'),
    path('resume/delete/section/<int:section_id>/', views.resume_delete_section, name='resume_delete_section'),

    # Generate & download
    path('resume/generate/', views.resume_generate, name='resume_generate'),
    path('resume/download/<int:resume_id>/', views.resume_download, name='resume_download'),
    path('resume/preview/<int:resume_id>/', views.resume_preview, name='resume_preview'),

    # List & delete generated resumes
    path('resume/list/', views.resume_list, name='resume_list'),
    path('resume/delete/generated/<int:resume_id>/', views.resume_delete_generated, name='resume_delete_generated'),

    # Get current profile JSON
    path('resume/profile/', views.resume_get_profile, name='resume_get_profile'),
    
    # Live on-the-fly preview
    path('resume/live-preview/', views.resume_live_preview, name='resume_live_preview'),

    # Separate resume exports history page
    path('resume/history/', views.resume_history, name='resume_history'),
    
    # Restore & Clear endpoints
    path('resume/restore/<int:resume_id>/', views.resume_restore, name='resume_restore'),
    path('resume/clear/', views.resume_clear, name='resume_clear'),
]

