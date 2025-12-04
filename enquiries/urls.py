from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_enquiry, name='submit_enquiry'),
    path('list/', views.enquiry_list, name='enquiry_list'),
    path('unread-count/', views.get_unread_count, name='unread_enquiry_count'),
]
