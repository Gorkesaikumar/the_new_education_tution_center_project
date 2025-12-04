from django.contrib import admin
from .models import StudyMaterial

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch', 'subject', 'uploaded_at', 'uploaded_by')
    list_filter = ('batch', 'subject', 'uploaded_at')
    search_fields = ('title', 'description')
