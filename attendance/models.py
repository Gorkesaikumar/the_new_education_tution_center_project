from django.db import models
from django.conf import settings

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    )
    date = models.DateField()
    batch = models.ForeignKey('batches.Batch', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_student': True})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')

    class Meta:
        unique_together = ('date', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"
