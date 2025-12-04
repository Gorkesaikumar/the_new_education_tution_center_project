from django.contrib import admin
from .models import Exam, Mark

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch', 'subject', 'date', 'total_marks')
    list_filter = ('batch', 'subject', 'date')
    search_fields = ('title',)

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained')
    list_filter = ('exam__batch', 'exam__subject')
    search_fields = ('student__username', 'exam__title')
