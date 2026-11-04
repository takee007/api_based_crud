from django.contrib import admin
from .models import StudentCV

@admin.register(StudentCV)
class StudentCVAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'student_id', 'email', 'education', 'created_at')
    search_fields = ('name', 'student_id', 'email')
    list_filter = ('education', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'passcode_hash')
