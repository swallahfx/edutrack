"""
Admin configuration for the assignments app.
"""

from django.contrib import admin
from .models import Assignment, Submission


class SubmissionInline(admin.TabularInline):
    """Inline admin for submissions within assignments."""
    model = Submission
    extra = 0
    readonly_fields = ['submitted_at', 'reviewed_at']
    autocomplete_fields = ['student']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for assignments."""
    list_display = ('title', 'course', 'due_date', 'points', 'submission_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'due_date', 'course')
    search_fields = ('title', 'description', 'course__title')
    autocomplete_fields = ['course']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SubmissionInline]
    
    def submission_count(self, obj):
        """Get submission count for the admin list display."""
        return obj.submissions.count()
    submission_count.short_description = 'Submissions'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for submissions."""
    list_display = ('student', 'assignment', 'submitted_at', 'status', 'is_late', 'reviewed_at')
    list_filter = ('status', 'submitted_at', 'reviewed_at', 'assignment__course')
    search_fields = ('student__username', 'assignment__title', 'content', 'feedback')
    readonly_fields = ['submitted_at', 'reviewed_at', 'is_late']
    autocomplete_fields = ['student', 'assignment']
    fieldsets = (
        (None, {
            'fields': ('assignment', 'student', 'content', 'file')
        }),
        ('Review', {
            'fields': ('status', 'feedback', 'reviewed_at')
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'is_late'),
            'classes': ('collapse',)
        }),
    )
