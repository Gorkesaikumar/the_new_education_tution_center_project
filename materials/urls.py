from django.urls import path
from . import views

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('upload/', views.material_upload, name='material_upload'),
    path('<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('my-materials/', views.student_materials, name='student_materials'),
]
