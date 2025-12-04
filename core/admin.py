from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Announcement

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_student', 'is_teacher')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'is_student', 'is_teacher')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_teacher')}),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_type', 'created_by', 'created_at')
    list_filter = ('target_type', 'created_at')
    search_fields = ('title', 'content')
