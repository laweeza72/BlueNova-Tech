from django.contrib import admin
from .models import (
    ResumeProfile, SocialNetwork, ResumeSection,
    EducationEntry, ExperienceEntry, ProjectEntry,
    PublicationEntry, SkillEntry, BulletEntry, NormalEntry,
    GeneratedResume,
)


class SocialNetworkInline(admin.TabularInline):
    model = SocialNetwork
    extra = 1


class ResumeSectionInline(admin.TabularInline):
    model = ResumeSection
    extra = 0
    show_change_link = True


@admin.register(ResumeProfile)
class ResumeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'selected_theme', 'updated_at')
    list_filter = ('selected_theme',)
    search_fields = ('user__username', 'full_name', 'email')
    inlines = [SocialNetworkInline, ResumeSectionInline]


@admin.register(ResumeSection)
class ResumeSectionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'title', 'entry_type', 'order')
    list_filter = ('entry_type',)


@admin.register(GeneratedResume)
class GeneratedResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'resume_name', 'theme', 'created_at')
    list_filter = ('theme',)
    readonly_fields = ('created_at',)
