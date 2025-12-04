from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'batch', 'status')
    list_filter = ('date', 'batch', 'status')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
