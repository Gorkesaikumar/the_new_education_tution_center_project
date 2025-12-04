from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.exam_create, name='exam_create'),
    path('<int:exam_id>/marks/', views.exam_marks, name='exam_marks'),
    path('my-marks/', views.student_marks, name='student_marks'),
]
