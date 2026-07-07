from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/applications/', views.admin_applications_view, name='admin_applications'),
    path('admin-dashboard/applications/action/<int:app_id>/<str:action_type>/', views.application_action_view, name='application_action'),
    path('admin-dashboard/applications/resume/<int:app_id>/', views.download_application_resume_view, name='download_application_resume'),
    
    # Profile Workspace
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_detail'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    
    # Document Workspace
    path('upload-files/', views.upload_file, name='upload_files'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    
    # User CRUD
    path('user-management/', views.user_management, name='user_management'),
    path('admin/api/user-action/', views.admin_user_action, name='admin_user_action'),
    path('admin/api/user-delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/api/user-details/<int:user_id>/', views.admin_user_details, name='admin_user_details'),
    path('api/check-status/', views.check_status_api, name='check_status_api'),
    path('api/system-state/', views.system_state_api, name='system_state_api'),
    
    # Correspondence
    path('messages/', views.messages_view, name='messages'),
    
    # Milestones & Alerts
    path('history/', views.history_view, name='history'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('delete-notification/<int:notif_id>/', views.delete_notification, name='delete_notification'),
    
    # Audit & Setup
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
    path('data-management/', views.data_management_view, name='data_management'),
    path('reset-database/', views.reset_database_view, name='reset_database'),
    
    # Support & Reviews
    path('help-center/', views.help_center_view, name='help_center'),
    path('feedback/', views.feedback_view, name='feedback'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    path('reports/csv/', views.export_csv_view, name='export_csv'),
    path('reports/pdf/', views.export_pdf_view, name='export_pdf'),
    
    # Global search and analytics
    path('search/', views.search_view, name='search'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/remove-picture/', views.remove_profile_picture, name='remove_profile_picture'),
    
    # Custom Admin APIs
    path('admin/api/users/action/', views.admin_user_action, name='admin_user_action'),
    path('admin/api/users/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/api/users/<int:user_id>/details/', views.admin_user_details, name='admin_user_details'),
    path('api/check-status/', views.check_status_api, name='check_status_api'),

    # Attendance Management Module
    path('attendance/dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('attendance/mark/', views.attendance_mark, name='attendance_mark'),
    path('attendance/list/', views.attendance_list, name='attendance_list'),
    path('attendance/details/<int:user_id>/', views.attendance_details, name='attendance_details'),
    path('attendance/export/csv/', views.attendance_export_csv, name='attendance_export_csv'),
    path('attendance/export/pdf/', views.attendance_export_pdf, name='attendance_export_pdf'),
    path('api/attendance/analytics/', views.attendance_analytics_api, name='attendance_analytics_api'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/attendance/csv/', views.attendance_export_own_csv, name='attendance_export_own_csv'),
    path('api/messages/send/', views.send_message_api, name='send_message_api'),
    path('api/messages/read/', views.mark_messages_read_api, name='mark_messages_read_api'),
]
