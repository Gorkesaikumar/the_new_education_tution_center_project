from django.db import models
from django.conf import settings

class FeePayment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    # In a real app, we might generate a PDF and store it, or generate it on the fly.
    # For now, let's just track the record.

    def __str__(self):
        return f"{self.student.username} - {self.amount} - {self.date}"
