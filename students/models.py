from django.db import models
from django.conf import settings
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    batch = models.ForeignKey('batches.Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_join = models.DateField(default=timezone.now)
    FEE_STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    )
    fee_status = models.CharField(max_length=10, choices=FEE_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.batch.name if self.batch else 'No Batch'}"
