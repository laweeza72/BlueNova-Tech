from django.contrib import admin
from .models import Profile, UploadedFile, Notification, Message, ActivityLog, Feedback, Setting, History, Report, Attendance

admin.site.register(Profile)
admin.site.register(UploadedFile)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(ActivityLog)
admin.site.register(Feedback)
admin.site.register(Setting)
admin.site.register(History)
admin.site.register(Report)
admin.site.register(Attendance)
