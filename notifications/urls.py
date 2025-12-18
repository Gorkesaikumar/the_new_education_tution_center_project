from django.urls import path
from . import views

urlpatterns = [
    path('save-token/', views.save_fcm_token, name='save_fcm_token'),
]
