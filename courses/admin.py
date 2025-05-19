"""
Admin configuration for the courses app.
"""

from django.contrib import admin
from .models import Course, Enrollment


class EnrollmentInline(admin.TabularInline):
    """Inline admin for enrollments within courses."""
    model = Enrollment
    extra = 0
    readonly_fields = ['enrolled_at']
    autocomplete_fields = ['student']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for courses."""
    list_display = ('title', 'teacher', 'enrollment_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'teacher__username')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['teacher']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EnrollmentInline]
    
    def enrollment_count(self, obj):
        """Get enrollment count for the admin list display."""
        return obj.students.count()
    enrollment_count.short_description = 'Enrollments'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for enrollments."""
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ['enrolled_at']
    autocomplete_fields = ['student', 'course']