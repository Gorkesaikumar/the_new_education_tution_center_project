from django.urls import path
from . import views

urlpatterns = [
    path('', views.fee_list, name='fee_list'),
    path('record/', views.record_payment, name='record_payment'),
    path('receipt/<int:pk>/', views.fee_receipt, name='fee_receipt'),
    path('my-fees/', views.my_fees, name='my_fees'),
]
