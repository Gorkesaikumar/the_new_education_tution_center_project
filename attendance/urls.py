from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('mark/<int:batch_id>/', views.mark_attendance, name='mark_attendance'),
    path('view/<int:batch_id>/', views.view_attendance, name='view_attendance'),
    path('my-attendance/', views.student_attendance, name='student_attendance'),
]
