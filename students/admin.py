from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'batch', 'phone_number', 'date_of_join')
    list_filter = ('batch', 'date_of_join')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')
