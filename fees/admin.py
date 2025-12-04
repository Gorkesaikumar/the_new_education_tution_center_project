from django.contrib import admin
from .models import FeePayment

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'date', 'transaction_id')
    list_filter = ('date',)
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'transaction_id', 'remarks')
